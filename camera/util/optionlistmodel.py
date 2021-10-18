"""Camera settings models."""

from camera.util.notify import Notifiable


class OptionListModel(Notifiable):
    """Creates a list model accessible trough indexes or values."""

    def __init__(self, model, value=0, index=-1):
        """Initialize the model object."""
        super().__init__(connectors=["previous", "next", "changed"])
        self.model = model
        if index < 0:
            self.__initial_value(value)
        else:
            self.__initial_index(index)

    @property
    def count(self):
        """Query the number of elements in the model."""
        return len(self.model)

    @property
    def value(self):
        """Retrieve the current value associated with the controller."""
        return self.model[self.current]

    def __initial_value(self, value):
        """Set the current value to closer valid value in the data model."""
        index = self.get_index_from_value(value)
        self.__initial_index(index)

    def __initial_index(self, index):
        """Set the current value to the given index."""
        assert 0 <= index >= 0 < self.count
        self.current = index

    def next(self):
        """Advance to next setting value."""
        if self.current < self.count - 1:
            self.current += 1
        self._notify(["next", "changed"])

    def previous(self):
        """Advance to next setting value."""
        if self.current > 0:
            self.current -= 1
        self._notify(["previous", "changed"])

    def get_index_from_value(self, value):
        """Retrieve the index of a value in the given model."""
        for i, v in enumerate(self.model):  # pylint: disable=invalid-name
            if value == v:
                return i
        return -1
