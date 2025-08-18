"""
Controller is the component that enables the interconnection between the views and
the model so it acts as an intermediary
"""

from model.model import modelConfig, VPC, Subnet
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

class controllerConfig:
    def __init__(self, model: modelConfig):
        self.model = model
        self.Session = sessionmaker(bind=model.engine)

    def get_all_vpcs(self):
        """Get all VPCs with their utilization scores"""
        session = self.Session()
        try:
            vpcs = session.query(VPC).all()
            result = []
            for vpc in vpcs:
                result.append({
                    'vpc_id': vpc.vpc_id,
                    'name': vpc.name,
                    'cidr_block': vpc.cidr_block,
                    'state': vpc.state,
                    'utilization_score': vpc.utilization_score,
                    'grade': self._score_to_grade(vpc.utilization_score),
                    'last_updated': vpc.last_updated.isoformat() if vpc.last_updated else None
                })
            return result
        except Exception as e:
            logger.error(f"Failed to get VPCs: {e}")
            raise
        finally:
            session.close()

    def get_vpc_details(self, vpc_id):
        """Get detailed VPC information including subnets"""
        session = self.Session()
        try:
            vpc = session.query(VPC).filter(VPC.vpc_id == vpc_id).first()
            if not vpc:
                return None
                
            subnets = session.query(Subnet).filter(Subnet.vpc_id == vpc_id).all()
            
            subnet_details = []
            for subnet in subnets:
                subnet_details.append({
                    'subnet_id': subnet.subnet_id,
                    'name': subnet.name,
                    'cidr_block': subnet.cidr_block,
                    'availability_zone': subnet.availability_zone,
                    'state': subnet.state,
                    'available_ip_count': subnet.available_ip_count,
                    'total_ip_count': subnet.total_ip_count,
                    'utilization_score': subnet.utilization_score,
                    'grade': self._score_to_grade(subnet.utilization_score)
                })
            
            return {
                'vpc_id': vpc.vpc_id,
                'name': vpc.name,
                'cidr_block': vpc.cidr_block,
                'state': vpc.state,
                'utilization_score': vpc.utilization_score,
                'grade': self._score_to_grade(vpc.utilization_score),
                'last_updated': vpc.last_updated.isoformat() if vpc.last_updated else None,
                'subnets': subnet_details
            }
        except Exception as e:
            logger.error(f"Failed to get VPC details for {vpc_id}: {e}")
            raise
        finally:
            session.close()

    def grade_vpc(self, vpc_id):
        """Get grading information for a specific VPC"""
        session = self.Session()
        try:
            vpc = session.query(VPC).filter(VPC.vpc_id == vpc_id).first()
            if not vpc:
                return None
                
            # Recalculate utilization to ensure it's current
            current_utilization = self.model.calculate_vpc_utilization(vpc_id)
            
            grade_info = self._calculate_grade_breakdown(vpc, current_utilization)
            return grade_info
            
        except Exception as e:
            logger.error(f"Failed to grade VPC {vpc_id}: {e}")
            raise
        finally:
            session.close()

    def refresh_data(self):
        """Refresh VPC data from AWS"""
        try:
            logger.info("Controller initiating data refresh...")
            self.model.update_db()
            return {"status": "success", "message": "Data refreshed successfully"}
        except Exception as e:
            logger.error(f"Failed to refresh data: {e}")
            return {"status": "error", "message": str(e)}

    def _score_to_grade(self, score):
        """Convert utilization score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'

    def _calculate_grade_breakdown(self, vpc, utilization_score):
        """Calculate detailed grading breakdown for a VPC"""
        session = self.Session()
        try:
            subnets = session.query(Subnet).filter(Subnet.vpc_id == vpc.vpc_id).all()
            
            # Grade factors
            utilization_grade = self._score_to_grade(utilization_score)
            
            # Efficiency: penalize if too few or too many subnets
            subnet_count = len(subnets)
            efficiency_score = 100
            if subnet_count < 2:
                efficiency_score = 50  # Single point of failure
            elif subnet_count > 10:
                efficiency_score = 70  # Possibly over-segmented
                
            # Cost optimization: lower scores for underutilized resources
            cost_score = min(utilization_score * 1.2, 100)
            
            # Overall grade (weighted average)
            overall_score = (utilization_score * 0.5 + efficiency_score * 0.3 + cost_score * 0.2)
            overall_grade = self._score_to_grade(overall_score)
            
            return {
                'vpc_id': vpc.vpc_id,
                'name': vpc.name,
                'overall_grade': overall_grade,
                'overall_score': round(overall_score, 2),
                'breakdown': {
                    'utilization': {
                        'score': utilization_score,
                        'grade': utilization_grade,
                        'weight': '50%'
                    },
                    'efficiency': {
                        'score': efficiency_score,
                        'grade': self._score_to_grade(efficiency_score),
                        'weight': '30%',
                        'factors': f'{subnet_count} subnets'
                    },
                    'cost_optimization': {
                        'score': round(cost_score, 2),
                        'grade': self._score_to_grade(cost_score),
                        'weight': '20%'
                    }
                },
                'recommendations': self._get_recommendations(utilization_score, efficiency_score, subnet_count)
            }
        finally:
            session.close()

    def _get_recommendations(self, utilization_score, efficiency_score, subnet_count):
        """Generate recommendations based on grades"""
        recommendations = []
        
        if utilization_score < 30:
            recommendations.append("Consider consolidating resources - very low utilization")
        elif utilization_score > 90:
            recommendations.append("High utilization - consider adding capacity")
            
        if subnet_count < 2:
            recommendations.append("Add subnets for redundancy and fault tolerance")
        elif subnet_count > 8:
            recommendations.append("Consider consolidating subnets to reduce complexity")
            
        if efficiency_score < 70:
            recommendations.append("Review subnet architecture for optimization")
            
        if not recommendations:
            recommendations.append("VPC is well-configured")
            
        return recommendations
