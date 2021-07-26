from savu.plugins.plugin_tools import PluginTools

class UnetApplyTools(PluginTools):
    """
    A simple plugin template with one in_dataset and one out_dataset with
    similar characteristics, e.g. median filter.
    """

    def define_parameters(self):
        """
        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data
            default: VOLUME_XZ
        model_file_path:
            visibility: basic
            dtype: str
            description: Path to the model file
            default: my_model.zip
        number_of_labels:
            visibility: basic
            dtype: int
            description: Number of labels in the segmentation
            default: 2
        """