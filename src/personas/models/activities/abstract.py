from personas.models.activities.insights import ActivityInsights


class Activity(object):
    def __init__(self,
                 activity_id: str,
                 source_name: str,
                 author_id: str = None,
                 enriched_properties: ActivityInsights = None
                 ) -> None:
        self.activity_id = activity_id
        self.source_name = source_name
        self.author_id = author_id
        self.enriched_properties = enriched_properties

    def __repr__(self):
        string = "ACTIVITY: "
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string
