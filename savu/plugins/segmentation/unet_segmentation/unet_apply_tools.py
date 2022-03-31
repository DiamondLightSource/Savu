from savu.plugins.plugin_tools import PluginTools

class UnetApplyTools(PluginTools):
    """
    A plugin with one in_dataset and one out_dataset that applies segmentation
    to the image data using a 2D U-Net model. 
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
        clip_data:
            visibility: intermediate
            dtype: bool
            description: Clip data
            default: True
        std_dev_factor:
            visibility: intermediate
            dtype: float
            description: Number of std devs from the mean to clip data to
            default: 2.575
        testing:
            visibility: advanced
            dtype: bool
            description: Switch on testing mode, model will be created in plugin rather than loaded
            default: False
        """