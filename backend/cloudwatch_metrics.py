"""
CloudWatch Metrics and Alarms for MediScan
This module handles custom metrics and alarms for AWS CloudWatch monitoring.
"""

import os
import time
import boto3
from typing import Optional
from functools import wraps


class CloudWatchMetrics:
    """Handles CloudWatch custom metrics and alarms."""
    
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        self.namespace = "MediScan"
        self.enabled = bool(self.aws_access_key and self.aws_secret_key and self.region)
        
        if self.enabled:
            self.cloudwatch = boto3.client(
                'cloudwatch',
                region_name=self.region,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )
        else:
            self.cloudwatch = None
    
    def put_metric(self, metric_name: str, value: float, unit: str = 'Count', 
                   dimensions: Optional[list] = None) -> bool:
        """
        Send a custom metric to CloudWatch.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement (Count, None, Seconds, etc.)
            dimensions: List of dimensions for the metric
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.cloudwatch:
            return False
        
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': int(time.time())
            }
            
            if dimensions:
                metric_data['Dimensions'] = dimensions
            
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
            return True
        except Exception as e:
            print(f"Failed to send metric {metric_name}: {e}")
            return False
    
    def put_counter(self, metric_name: str, value: int = 1, 
                    dimensions: Optional[list] = None) -> bool:
        """Convenience method for counter metrics."""
        return self.put_metric(metric_name, float(value), 'Count', dimensions)
    
    def put_gauge(self, metric_name: str, value: float,
                  dimensions: Optional[list] = None) -> bool:
        """Convenience method for gauge metrics."""
        return self.put_metric(metric_name, value, 'None', dimensions)
    
    def create_alarm(self, alarm_name: str, metric_name: str, 
                     threshold: float, comparison_operator: str,
                     evaluation_periods: int = 1, period: int = 300,
                     statistic: str = 'Average',
                     dimensions: Optional[list] = None,
                     alarm_description: str = "") -> bool:
        """
        Create a CloudWatch alarm.
        
        Args:
            alarm_name: Unique name for the alarm
            metric_name: Name of the metric to monitor
            threshold: Alarm threshold value
            comparison_operator: GreaterThanThreshold, LessThanThreshold, etc.
            evaluation_periods: Number of periods to evaluate
            period: Period in seconds (default: 300 = 5 minutes)
            statistic: Statistic to use (Average, Sum, Maximum, etc.)
            dimensions: Metric dimensions
            alarm_description: Description of the alarm
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.cloudwatch:
            return False
        
        try:
            alarm_params = {
                'AlarmName': alarm_name,
                'AlarmDescription': alarm_description,
                'ActionsEnabled': True,
                'MetricName': metric_name,
                'Namespace': self.namespace,
                'Statistic': statistic,
                'Period': period,
                'EvaluationPeriods': evaluation_periods,
                'Threshold': threshold,
                'ComparisonOperator': comparison_operator
            }
            
            if dimensions:
                alarm_params['Dimensions'] = dimensions
            
            self.cloudwatch.put_metric_alarm(**alarm_params)
            return True
        except Exception as e:
            print(f"Failed to create alarm {alarm_name}: {e}")
            return False


# Global instance
metrics = CloudWatchMetrics()


def track_request(metric_name: str = "APIRequest"):
    """Decorator to track API requests in CloudWatch."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            finally:
                duration = time.time() - start_time
                metrics.put_counter(metric_name, 1)
                metrics.put_gauge(f"{metric_name}Duration", duration)
                
                if not success:
                    metrics.put_counter(f"{metricName}Error", 1)
        
        return wrapper
    return decorator


def setup_standard_alarms():
    """Set up standard CloudWatch alarms for the application."""
    if not metrics.enabled:
        return
    
    # High error rate alarm
    metrics.create_alarm(
        alarm_name="MediScan-HighErrorRate",
        metric_name="APIRequestError",
        threshold=10,
        comparison_operator="GreaterThanThreshold",
        evaluation_periods=2,
        period=300,
        statistic="Sum",
        alarm_description="Alert when error rate exceeds 10 errors in 5 minutes"
    )
    
    # High response time alarm
    metrics.create_alarm(
        alarm_name="MediScan-HighResponseTime",
        metric_name="APIRequestDuration",
        threshold=2.0,
        comparison_operator="GreaterThanThreshold",
        evaluation_periods=2,
        period=300,
        statistic="Average",
        alarm_description="Alert when average response time exceeds 2 seconds"
    )
    
    # Low request rate alarm (optional)
    metrics.create_alarm(
        alarm_name="MediScan-LowRequestRate",
        metric_name="APIRequest",
        threshold=1,
        comparison_operator="LessThanThreshold",
        evaluation_periods=12,
        period=300,
        statistic="Sum",
        alarm_description="Alert when request rate drops below 1 request per hour"
    )
    
    print("CloudWatch alarms configured successfully")


if __name__ == "__main__":
    # Test the metrics
    print(f"CloudWatch enabled: {metrics.enabled}")
    
    if metrics.enabled:
        metrics.put_counter("TestMetric", 1)
        metrics.put_gauge("TestGauge", 42.5)
        setup_standard_alarms()
        print("Metrics test completed")
    else:
        print("CloudWatch is not configured. Set AWS credentials to enable.")
