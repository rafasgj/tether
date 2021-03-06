"""Camera settings models."""


class OptionListModel(object):
    """Creates a list model accessible trough indexes or values."""

    def __init__(self, model, value=0, index=-1):
        """Initialize the model object."""
        self.model = model
        if index < 0:
            self.__initial_value(value)
        else:
            self.__initial_index(index)

    def __initial_value(self, value):
        """Set the current value to closer valid value in the data model."""
        index = self.get_index_from_value(self.model, value)
        self.__initial_index(index)

    def __initial_index(self, index):
        """Set the current value to the given index."""
        assert index >= 0 and index < len(self.model)
        self.current = index

    def next(self):
        """Advance to next setting value."""
        if self.current < len(self.model) - 1:
            self.current += 1

    def previous(self):
        """Advance to next setting value."""
        if self.current > 0:
            self.current -= 1

    @staticmethod
    def get_index_from_value(model, value):
        """Retrieve the index of a value in the given model."""
        for i, v in enumerate(model):
            if value == v:
                return i
        else:
            return -1

    @property
    def value(self):
        """Retrieve the current value associated with the controller."""
        return self.model[self.current]
