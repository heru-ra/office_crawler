
class Generator:

    def __init__(self, end: int = 100, row_length: int = 20):

        self.end = end + 1
        self.row_length = row_length

    def calc_exits(self, num: int, direction: str):

        if direction == 'n':
            num = num - self.row_length
            if num <= 0:
                return 'null'
            else:
                return num

        elif direction == 's':
            num = num + self.row_length
            if num >= self.end:
                return 'null'
            else:
                return num

        elif direction == 'w':
            if (num - 1) % self.row_length == 0:
                return 'null'
            else:
                return num - 1

        elif direction == 'e':
            if num % self.row_length == 0:
                return 'null'
            else:
                return num + 1

    def create(self):

        total_lines = ""

        for num in range(1, self.end):

            n = self.calc_exits(num, 'n')
            s = self.calc_exits(num, 's')
            w = self.calc_exits(num, 'w')
            e = self.calc_exits(num, 'e')

            exits = f"{{\"north\": {n}, \"south\": {s}, \"west\": {w}, \"east\": {e}}}"

            line = f"\"{num}\": {{" \
                f"\"name\": \"A Room Marked '#{num}'\"," \
                f"\"exits\": {exits}," \
                f"\"desc\": \"The walls and floor of this room are a " \
                f"bright, sterile white. You feel as if you are inside a " \
                f"simulation.\"}}"

            if num == (self.end - 1):
                total_lines = f"{total_lines}{line}"
            else:
                total_lines = f"{total_lines}{line},"

        total_lines = f"{{{total_lines}}}"

        map_file = open('office_map_new', 'w+')
        map_file.write(total_lines)
        map_file.close()


if __name__ == '__main__':

    new_map = Generator(506, 22)
    new_map.create()
