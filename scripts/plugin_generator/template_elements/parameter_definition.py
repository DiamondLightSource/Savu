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
            dependency:
                parameter_name_1: [3, 9]
        """

    def citation1(self):
        # use a u notation for unicode characters - for example, mew
        """
        A description of the citation
        bibtex:
                A bibtex string.
        endnote:
                An endnote string.
        doi: A link in the form of numbers and letters
        dependency:
            parameter_name_1: The name of the method for which this citation is for
        """