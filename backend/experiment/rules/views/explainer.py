class Explainer(object):
    """
    Provide data for a explainer that explains the experiment steps

    Relates to client component: Explainer.js    
    """

    ID = "EXPLAINER"

    def __init__(self, instruction, steps, button_label="Let's go!"):
        self.instruction = instruction
        self.steps = steps
        self.button_label = button_label

    def action(self, step_numbers=False):
        """Get data for explainer action"""
        if step_numbers:
            serialized_steps = [step.action(index+1) for index, step in enumerate(self.steps)]
        else:
            serialized_steps = [step.action() for step in self.steps]
        return {
            'view': self.ID,
            'instruction': self.instruction,
            'button_label': self.button_label,
            'steps': serialized_steps,
        }


class Step(object):

    def __init__(self, description):
        self.description = description

    def action(self, number=None):
        """Create an explainer step, with description and optional number"""
        return {
            'number': number,
            'description': self.description
        }
