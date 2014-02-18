import time
import datetime


class Xhprof:
    def __init__(self, mongodb):
        self.mongodb = mongodb

    def save(self, name, stats):
        microtime = time.time()
        sec = int(microtime)
        result = {
            'profile': get_xhprof_data(stats),
            'meta': {
                'url': name,
                'simple_url': name,
                'SERVER': {
                    'REQUEST_TIME': sec
                },
                'request_ts': datetime.datetime.now(),
                'request_date': datetime.date.today().strftime('%Y-%m-%d')
            }
        }
        self.mongodb.results.save(result)


def get_xhprof_data(stats):

    def full(name):
        module, lineno, func_name = name
        func_name = func_name.replace('.', '::')
        return func_name

    data = {}
    data['main()'] = {
        'ct': 1,
        'wt': 0,
        'cpu': 0,
        'mu': 0,
        'pmu': 0,
    }
    for name, stat in stats.stats.items():
        (call, actualcall, inclusive, exclusive, parents) = stat
        inclusive = int(1000000 * inclusive)
        for p_name, p_stat in parents.items():
            (p_call, p_actualcall, p_inclusive, p_exclusive) = p_stat
            p_inclusive = int(1000000 * p_inclusive)
            data['{0}==>{1}'.format(full(p_name), full(name))] = {
                'ct': p_call,
                'wt': p_inclusive,
                'cpu': p_inclusive,
                'mu': 0,
                'pmu': 0,
            }
            call -= p_call
            inclusive -= p_inclusive
        if call > 0:
            data['main()==>{0}'.format(full(name))] = {
                'ct': call,
                'wt': inclusive,
                'cpu': inclusive,
                'mu': 0,
                'pmu': 0,
            }
            data['main()']['wt'] += inclusive
            data['main()']['cpu'] += inclusive

    return data
