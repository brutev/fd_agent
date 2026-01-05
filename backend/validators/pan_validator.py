from .ifsc_validator import PANValidator

class PANValidator:
    """PAN Card validator with checksum verification"""
    
    @staticmethod
    def validate(pan: str) -> bool:
        """Validate PAN format: 5 letters + 4 digits + 1 letter"""
        if not pan or len(pan) != 10:
            return False
        
        import re
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        return bool(re.match(pattern, pan.upper()))
    
    @staticmethod
    def extract_entity_type(pan: str) -> str:
        """Extract entity type from PAN's 4th character"""
        if not PANValidator.validate(pan):
            return "Invalid"
        
        entity_map = {
            'P': 'Individual',
            'C': 'Company',
            'H': 'HUF',
            'F': 'Firm',
            'A': 'AOP',
            'T': 'Trust',
            'B': 'Body of Individuals',
            'L': 'Local Authority',
            'J': 'Artificial Juridical Person',
            'G': 'Government'
        }
        
        return entity_map.get(pan[3].upper(), 'Unknown')