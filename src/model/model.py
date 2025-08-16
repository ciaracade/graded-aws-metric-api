"""
Model corresponds to all the data-related logic that the user works with
transferred between the View and Controller components or etc.
"""

from aws.config import AWSConfig
from sqlalchemy import create_engine, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

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
    subnets: Mapped[list["Subnet"]] = relationship("Subnet", foreign_keys="Subnet.vpc_id")
    

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


# we want have every subnet and calculate based on (total - avail) / total 

class modelConfig:
    def __init__(self, client: AWSConfig):
        self.client = client
        self.engine = create_engine("sqlite:///db/metrics.db")
        Base.metadata.create_all(self.engine)
        self.seed_db()
    
    def seed_db(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        vpcs = self.client.describe_vpcs()
        subnets = self.client.describe_subnets()

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
            session.add(db_subnet)
            
        session.commit()
        session.close()