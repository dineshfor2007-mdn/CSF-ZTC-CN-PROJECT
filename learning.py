class OnlineLearning:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.history = {}

    def update(self, network):
        for name, link in network.links.items():
            traffic = link["traffic"]

            if name not in self.history:
                self.history[name] = traffic
            else:
                self.history[name] = (
                    self.alpha * traffic
                    + (1 - self.alpha) * self.history[name]
                )

    def get_prediction(self, link_name):
        return self.history.get(link_name, 0.0)