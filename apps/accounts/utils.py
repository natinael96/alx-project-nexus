"""
Utility functions for accounts app.
"""
from typing import Dict


def calculate_profile_completion(user) -> Dict:
    """
    Calculate user profile completion percentage.
    
    Returns:
        Dictionary with completion percentage and missing fields.
    """
    total_fields = 0
    completed_fields = 0
    missing_fields = []
    
    # Basic profile fields
    basic_fields = [
        ('first_name', 'First Name'),
        ('last_name', 'Last Name'),
        ('email', 'Email'),
        ('phone_number', 'Phone Number'),
        ('bio', 'Bio'),
        ('profile_picture', 'Profile Picture'),
    ]
    
    for field_name, field_label in basic_fields:
        total_fields += 1
        if getattr(user, field_name, None):
            completed_fields += 1
        else:
            missing_fields.append(field_label)
    
    # Skills
    total_fields += 1
    if user.skills.exists():
        completed_fields += 1
    else:
        missing_fields.append('Skills')
    
    # Education
    total_fields += 1
    if user.education.exists():
        completed_fields += 1
    else:
        missing_fields.append('Education')
    
    # Work History
    total_fields += 1
    if user.work_history.exists():
        completed_fields += 1
    else:
        missing_fields.append('Work History')
    
    # Portfolio (optional but counts)
    total_fields += 1
    if user.portfolio.exists():
        completed_fields += 1
    else:
        missing_fields.append('Portfolio (Optional)')
    
    # Social Links (optional)
    total_fields += 1
    if user.social_links.exists():
        completed_fields += 1
    
    # Calculate percentage
    percentage = int((completed_fields / total_fields) * 100) if total_fields > 0 else 0
    
    return {
        'percentage': percentage,
        'completed_fields': completed_fields,
        'total_fields': total_fields,
        'missing_fields': missing_fields,
        'is_complete': percentage >= 80  # Consider 80%+ as complete
    }
