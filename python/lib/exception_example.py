from decimal import DivisionByZero


class GaryException(Exception):
    pass

def inner():
    raise GaryException('there was an error')
    print('after error')

def main():
    try:
        inner()
        test = 1/0
    except ZeroDivisionError:
        print('maths error!')




if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('oops',  e)

    print('some other processing!')