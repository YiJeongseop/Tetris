
class TimeTracking:
    def __init__(self):
        self.avg_time = 0
        self.total_time = 0 
        self.start_time = 0

    def update_time(self, time: float, block_count: int):
        """
        Updates the total time and average time to put a block.
        """
        self.total_time += (time - self.start_time)
        self.avg_time = self.total_time / block_count
