"""
Model corresponds to all the data-related logic that the user works with
transferred between the View and Controller components or etc.
"""

from aws.config import AWSConfig
from sqlalchemy import create_engine, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create ORM mapped classes 
class Base(DeclarativeBase):
    pass

class Account(Base):
    __tablename__="account"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer)

class VPC(Base):
    __tablename__="vpc"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    vpc_id: Mapped[str] = mapped_column(String(50))
    account_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(20))
    cidr_block: Mapped[str] = mapped_column(String(18))
    state: Mapped[str] = mapped_column(String(20))
    utilization_score: Mapped[int] = mapped_column(Integer, default=0)
    subnets: Mapped[list["Subnet"]] = relationship("Subnet", foreign_keys="Subnet.vpc_id")
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    

class Subnet(Base):
    __tablename__="subnet"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    subnet_id: Mapped[str] = mapped_column(String(50))
    vpc_id: Mapped[str] = mapped_column(String(50), ForeignKey("vpc.vpc_id"))
    account_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(20))
    cidr_block: Mapped[str] = mapped_column(String(18))
    state: Mapped[str] = mapped_column(String(20))
    availability_zone: Mapped[str] = mapped_column(String(20))
    available_ip_count: Mapped[int] = mapped_column(Integer)
    total_ip_count: Mapped[int] = mapped_column(Integer)
    utilization_score: Mapped[int] = mapped_column(Integer)
    last_updated: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow)


# we want have every subnet and calculate based on (total - avail) / total 

class modelConfig:
    def __init__(self, client: AWSConfig):
        self.client = client
        self.engine = create_engine("sqlite:///db/metrics.db")
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")
        self.update_db()
    
    def calculate_vpc_utilization(self, vpc_id):
        """Calculate VPC utilization based on its subnets"""
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        try:
            vpc = session.query(VPC).filter(VPC.vpc_id == vpc_id).first()
            if not vpc:
                return 0
                
            subnets = session.query(Subnet).filter(Subnet.vpc_id == vpc_id).all()
            if not subnets:
                return 0
                
            # Calculate weighted average based on subnet sizes
            total_ips = sum(subnet.total_ip_count for subnet in subnets)
            if total_ips == 0:
                return 0
                
            weighted_utilization = sum(
                subnet.utilization_score * (subnet.total_ip_count / total_ips) 
                for subnet in subnets
            )
            
            # Update VPC utilization score
            vpc.utilization_score = round(weighted_utilization, 2)
            session.commit()
            
            return vpc.utilization_score
            
        except Exception as e:
            logger.error(f"Failed to calculate VPC utilization for {vpc_id}: {e}")
            session.rollback()
            return 0
        finally:
            session.close()
    
    def seed_db(self):
        logger.info("Starting database seeding...")
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        try:
            vpcs = self.client.describe_vpcs()
            subnets = self.client.describe_subnets()
            logger.info(f"Retrieved {len(vpcs.get('Vpcs', []))} VPCs and {len(subnets.get('Subnets', []))} subnets from AWS")

            for vpc in vpcs.get('Vpcs'):
                name = 'unknown'
                for tag in vpc.get('Tags', []):
                    if tag.get('Key') == 'Name':
                        name = tag.get('Value', 'unknown')
                        break
                        
                db_vpc = VPC(
                    vpc_id=vpc['VpcId'],
                    account_id=int(vpc.get('OwnerId', 0)),
                    name=name,
                    cidr_block=vpc['CidrBlock'],
                    state=vpc['State'],
                )
                session.add(db_vpc)
                logger.info(f"Added VPC: {vpc['VpcId']} ({name})")
            
            for subnet in subnets.get('Subnets'):
                name = 'unknown'
                for tag in subnet.get('Tags', []):
                    if tag.get('Key') == 'Name':
                        name = tag.get('Value', 'unknown')
                        break
                        
                db_subnet = Subnet(
                    subnet_id=subnet['SubnetId'],
                    vpc_id=subnet['VpcId'],
                    account_id=int(subnet.get('OwnerId', 0)),
                    name=name,
                    cidr_block=subnet['CidrBlock'],
                    state=subnet['State'],
                    availability_zone=subnet['AvailabilityZone'],
                    available_ip_count=subnet['AvailableIpAddressCount'],
                    total_ip_count=2**(32 - int(subnet['CidrBlock'].split('/')[1])),
                    utilization_score=0
                )
                
                # calculate subnet utilization score
                total_ips = db_subnet.total_ip_count
                used_ips = total_ips - subnet['AvailableIpAddressCount']
                if total_ips > 0:
                    utilization_percentage = (used_ips / total_ips) * 100
                    db_subnet.utilization_score = round(utilization_percentage, 2)
                
                session.add(db_subnet)
                logger.info(f"Added Subnet: {subnet['SubnetId']} ({name}) - {subnet['AvailableIpAddressCount']} IPs available")
            
            session.commit()
            
            # calculate VPC utilization scores after all subnets are added
            logger.info("Calculating VPC utilization scores...")
            for vpc in vpcs.get('Vpcs'):
                utilization = self.calculate_vpc_utilization(vpc['VpcId'])
                logger.info(f"VPC {vpc['VpcId']} utilization: {utilization}%")
            
            logger.info("Database seeding completed successfully")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to seed database: {e}")
            raise
        finally:
            session.close()
    
    def update_db(self):
        logger.info("Starting database update...")
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        try:
            # Clear existing data
            subnet_count = session.query(Subnet).count()
            vpc_count = session.query(VPC).count()
            logger.info(f"Clearing {subnet_count} subnets and {vpc_count} VPCs from database")
            
            session.query(Subnet).delete()
            session.query(VPC).delete()
            session.commit()
            session.close()
            
            # Reseed with fresh data
            logger.info("Reseeding database with fresh AWS data...")
            self.seed_db()
            logger.info("Database update completed successfully")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update database: {e}")
            raise
        finally:
            if session:
                session.close()