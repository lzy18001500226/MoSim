import sys
from ui import View
def exec():

    path = sys.argv[1]
    topic_field_pairs = [(sys.argv[i], sys.argv[i + 1]) for i in range(2, len(sys.argv), 2)]
    print(topic_field_pairs)
    view = View(path, topic_field_pairs)
    view.show()

if __name__ == '__main__':
    exec()