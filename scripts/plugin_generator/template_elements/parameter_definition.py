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

    def get_citation(self):
        """
        citation1:
            description: A description of the citation
            bibtex: |
                    A bibtex string with the symbol '|' on the above line to
                    maintain the multiple new line format.
            endnote: |
                    An endnote string with the symbol '|' on the above line to
                    maintain the multiple new line format.
            doi: A link in the form of numbers and letters
            dependency:
                parameter_name_1: The name of the method for which this citation is for
        """