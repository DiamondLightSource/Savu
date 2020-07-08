    def define_parameters(self):
        """
        parameter_name_1:
            visibility: basic
            dtype: int
            description: "Describe your parameter"
            default: 1

        parameter_name_2:
            visibility: intermediate
            dtype: str
            description: "Describe your parameter"
            default: A default value
            options: [A default value, option1, option2, option3]
            dependencies:
                parameter_name_1: [3, 9]
        """

    def get_bibtex(self):
        """
        @article{
        }
        """

    def get_endnote(self):
        """
        %0 Journal Article
        """