from pathlib import Path

from visual_stim.base import BaseMeta

MISSING_VALUE = 9999

class Session(BaseMeta):
    """
    Represents a single session, mainly its behavioural data.
    """

    def __init__(self, name=None, data_dir=None, meta_dir=None, cache_dir=None):
        super().__init__(meta_dir, name=name)
        self.cache_dir = cache_dir
        self.data_dir = data_dir


    @classmethod
    def get_session(cls, mouse_dir=None, name=None, cache_dir=None):
        """
        Initialise a Session object from behavioural data file.

        params
        ===
        mouse_dir: str, directory to behavioural training data of a session
        from a experimental mouse.
        """
        if mouse_dir is None or name is None:
            raise ValueError("mouse_dir and name must be provided.")

        mouse_dir = Path(mouse_dir)

        if not mouse_dir.is_dir():
            raise NotADirectoryError(
                f"Mouse directory does not exist or is not a directory: {mouse_dir}"
            )

        ses_dir = mouse_dir / name
        matches = sorted(ses_dir.glob(f"*{name}*meta*"))

        if not matches:
            raise FileNotFoundError(
                f"No metadata matching '*{name}*meta*' found in {ses_dir}"
            )

        if len(matches) > 1:
            raise ValueError(
                f"Multiple metadata matches for session {name!r}: {matches}"
            )

        return cls(
            name=name,
            data_dir=ses_dir,
            meta_dir=matches[0],
            cache_dir=cache_dir,
        )


    def extract_trials(self):

        """
        Write getting trial data as a separate function to deal with .mat file
        so that the same code can be reused.

        return
        ===
        output: 
        """
        # TODO nov 11 continue here

