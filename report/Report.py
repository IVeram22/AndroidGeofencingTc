class Graph:

    def __init__(self, id_graph: str, title: str, label: str, begin_at_zero: bool, border_color: str, x_title: str,
                 y_title: str):
        self.id_graph = id_graph
        self.title = title
        self.label = label
        self.begin_at_zero = begin_at_zero
        self.border_color = border_color
        self.x_data = []
        self.x_title = x_title
        self.y_data = []
        self.y_title = y_title

    def add_data(self, x, y):
        self.x_data.append(x)
        self.y_data.append(y)

    def __str__(self):
        return "\"id_graph\": {}, \"title\": {}, \"label\": {}, \"begin_at_zero\": {}, \"border_color\": {}, " \
               "\"x_data\": {}, \"x_title\": {}, \"y_data\": {}, \"y_title\": {}" \
            .format(self.id_graph, self.title, self.label, self.begin_at_zero, self.border_color, self.x_data,
                    self.x_title, self.y_data, self.y_title)


class Fails:
    def __init__(self, action: str, img_path: str):
        self.action = action
        self.img_path = img_path


class Report:
    def __init__(self, test_name: str, test_time: float):
        self.test_name = test_name
        self.test_time = test_time
        self.graphs = []
        self.fails = []
        self.conclusions = ""

    def add_graph(self, id_graph: str, title: str, label: str, begin_at_zero: bool, border_color: str, x_title: str,
                  y_title: str):
        self.graphs.append(Graph(id_graph, title, label, begin_at_zero, border_color, x_title, y_title))

    def get_graph(self, id_graph: str):
        for graph in self.graphs:
            if graph.id_graph == id_graph:
                return graph
        return None

    def add_fails(self, action: str, img_path: str):
        self.fails.append(
            Fails(action, img_path)
        )

    def __str__(self):
        json_str = "{\n"
        json_str += "\t\"test_name\": \"%s\", \n" % self.test_name
        json_str += "\t\"test_time\": \"%s\", \n" % self.test_time
        json_str += "\t\"conclusions\": \"%s\", \n" % self.conclusions
        json_str += "\t\"graphs\": [\n"
        size = len(self.graphs)
        for graph in self.graphs:
            json_str += "\t{ \n"
            json_str += "\t\t\"id_graph\": \"%s\", \n" % graph.id_graph
            json_str += "\t\t\"title\": \"%s\", \n" % graph.title
            json_str += "\t\t\"label\": \"%s\", \n" % graph.label
            json_str += "\t\t\"begin_at_zero\": \"%s\", \n" % graph.begin_at_zero
            json_str += "\t\t\"border_color\": \"%s\", \n" % graph.border_color
            json_str += "\t\t\"x_data\": %s, \n" % graph.x_data
            json_str += "\t\t\"x_title\": \"%s\", \n" % graph.x_title
            json_str += "\t\t\"y_data\": %s, \n" % graph.y_data
            json_str += "\t\t\"y_title\": \"%s\"\n" % graph.y_title
            size -= 1
            if size <= 0:
                json_str += "\t }"
            else:
                json_str += "\t },\n"
        json_str += "],\n"

        json_str += "\t\"fails\": [\n"
        size = len(self.fails)
        for fail in self.fails:
            json_str += "\t{ \n"
            json_str += "\t\t\"action\": \"%s\", \n" % fail.action
            json_str += "\t\t\"img_path\": \"/root/MyProjects/ArloAutomationServer/%s\" \n" % fail.img_path
            size -= 1
            if size <= 0:
                json_str += "\t }"
            else:
                json_str += "\t },\n"
        json_str += "]\n"
        json_str += "}"
        return json_str
