import epicbox

epicbox.configure(
    profiles=[
        epicbox.Profile('python', 'python:3.6.5-alpine')
    ]
)
files = [{'name': 'main.py', 'content': b'print(43)'}]
limits = {'cputime': 1, 'memory': 64}
result = epicbox.run('python', 'python3 main.py', files=files, limits=limits)
print(result)
