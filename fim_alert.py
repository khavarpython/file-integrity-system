import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import configparser
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='fim_alerts.log'
)

class FIMAlertManager:
    """
    Alert mechanism for File Integrity Monitoring system
    Handles email notifications when file integrity changes are detected
    """
    
    def __init__(self, config_file='alert_config.ini'):
        """
        Initialize the alert manager with configuration settings
        
        Args:
            config_file (str): Path to the configuration file
        """
        self.config = self._load_config(config_file)
        self.email_config = {
            'smtp_server': self.config.get('Email', 'smtp_server'),
            'smtp_port': self.config.getint('Email', 'smtp_port'),
            'sender_email': self.config.get('Email', 'sender_email'),
            'sender_password': self.config.get('Email', 'sender_password'),
            'recipient_emails': json.loads(self.config.get('Email', 'recipient_emails'))
        }
        
        # Alert throttling settings
        self.alert_history = {}
        self.throttle_period = self.config.getint('Throttling', 'throttle_period_seconds', fallback=300)
        
        logging.info("FIM Alert Manager initialized")
    
    def _load_config(self, config_file):
        """
        Load configuration from file or create default if not exists
        
        Args:
            config_file (str): Path to configuration file
            
        Returns:
            ConfigParser: Configuration object
        """
        config = configparser.ConfigParser()
        
        if not os.path.exists(config_file):
            # Create default configuration
            config['Email'] = {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': '587',
                'sender_email': 'your_email@gmail.com',
                'sender_password': 'your_app_password',
                'recipient_emails': '["admin@example.com", "security@example.com"]'
            }
            
            config['Throttling'] = {
                'throttle_period_seconds': '300',  # 5 minutes
                'max_alerts_per_file': '3'
            }
            
            config['AlertLevels'] = {
                'file_modified': 'MEDIUM',
                'file_created': 'LOW',
                'file_deleted': 'HIGH'
            }
            
            # Write default config to file
            with open(config_file, 'w') as f:
                config.write(f)
            
            logging.info(f"Created default configuration file: {config_file}")
        else:
            config.read(config_file)
        
        return config
    
    def send_alert(self, event_type, file_path, details=None):
        """
        Send alert notification based on the event type
        
        Args:
            event_type (str): Type of file event (modified, created, deleted)
            file_path (str): Path of the affected file
            details (dict, optional): Additional details about the event
        
        Returns:
            bool: True if alert was sent successfully, False otherwise
        """
        # Check if we should throttle this alert
        if not self._should_send_alert(file_path):
            logging.info(f"Alert throttled for {file_path}")
            return False
            
        # Get alert level based on event type
        alert_level = self.config.get('AlertLevels', event_type.lower(), fallback='MEDIUM')
        
        # Create alert message
        subject = f"FIM ALERT [{alert_level}]: File {event_type} - {os.path.basename(file_path)}"
        
        # Build message body
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = f"""
        File Integrity Monitoring Alert
        ==============================
        Event Type: {event_type}
        Alert Level: {alert_level}
        Timestamp: {timestamp}
        File Path: {file_path}
        """
        
        if details:
            body += "\nAdditional Details:\n"
            for key, value in details.items():
                body += f"{key}: {value}\n"
        
        # Send email alert
        try:
            self._send_email(subject, body)
            logging.info(f"Alert sent for {event_type} on {file_path}")
            
            # Update alert history for throttling
            self._update_alert_history(file_path)
            return True
            
        except Exception as e:
            logging.error(f"Failed to send alert: {str(e)}")
            return False
    
    def _send_email(self, subject, body):
        """
        Send email using configured SMTP settings
        
        Args:
            subject (str): Email subject
            body (str): Email body
        """
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.email_config['sender_email']
        msg['To'] = ', '.join(self.email_config['recipient_emails'])
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server and send
        with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            server.send_message(msg)
    
    def _should_send_alert(self, file_path):
        """
        Determine if an alert should be sent based on throttling rules
        
        Args:
            file_path (str): Path of the file
            
        Returns:
            bool: True if alert should be sent, False if it should be throttled
        """
        current_time = datetime.now().timestamp()
        max_alerts = self.config.getint('Throttling', 'max_alerts_per_file', fallback=3)
        
        if file_path in self.alert_history:
            last_alert_time, alert_count = self.alert_history[file_path]
            
            # If within throttle period
            if current_time - last_alert_time < self.throttle_period:
                # Allow if under max alerts
                if alert_count < max_alerts:
                    return True
                else:
                    return False
            else:
                # Reset counter if outside throttle period
                return True
        else:
            # First alert for this file
            return True
    
    def _update_alert_history(self, file_path):
        """
        Update the alert history for a file
        
        Args:
            file_path (str): Path of the file
        """
        current_time = datetime.now().timestamp()
        
        if file_path in self.alert_history:
            last_time, count = self.alert_history[file_path]
            
            # If within throttle period, increment counter
            if current_time - last_time < self.throttle_period:
                self.alert_history[file_path] = (current_time, count + 1)
            else:
                # Reset counter if outside throttle period
                self.alert_history[file_path] = (current_time, 1)
        else:
            # First alert for this file
            self.alert_history[file_path] = (current_time, 1)

# Example of how this would integrate with Watchdog events
def handle_watchdog_event(event_type, file_path, old_hash=None, new_hash=None):
    """
    Handle events from the Watchdog-based monitoring system
    
    Args:
        event_type (str): Type of event (modified, created, deleted)
        file_path (str): Path of the affected file
        old_hash (str, optional): Previous hash value for modified files
        new_hash (str, optional): New hash value for modified files
    """
    alert_manager = FIMAlertManager()
    
    details = {}
    if old_hash and new_hash:
        details = {
            "Previous Hash": old_hash,
            "Current Hash": new_hash
        }
    
    alert_manager.send_alert(event_type, file_path, details)

# EXAMPLE USAGE FOR BRIANA
if __name__ == "__main__":
    # This demonstrates how the module would be used in part 3 code
    # Simulate a file modification event

    handle_watchdog_event(
        "modified",  # event type
        "/etc/passwd",  # file path
        old_hash="abc123", # old hash
        new_hash="def456" # new hash
    )