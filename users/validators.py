from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ComplexityValidator:

    def validate(self,password,user=None):
        minimum_requirement = 1
        capitals = [char for char in password if char.isupper()]
        lowers = [char for char in password if char.islower()]
        numbers = [char for char in password if char.isdigit()]
        special = [char for char in password if not char.isalnum()]

        if(len(capitals) < minimum_requirement or len(lowers) < minimum_requirement or len(numbers) < minimum_requirement or len(special) < minimum_requirement):
            raise ValidationError(
                _("you will need at least one uppercase letter, one lowercase letter, one number, one non-word charcter"),
                code ="you will need at least one uppercase letter, one lowercase letter, one number, one non-word charcter"
            )
        
class CharacterRepeatValidator:
    def validate(self, password, user=None):
        for char in password:
            if char * 3 in password:
                raise ValidationError(
                    _("YOu cannot repeat one character more than two times in succssion!"),
                    code = "YOu cannot repeat one character more than two times in succssion!"
                )