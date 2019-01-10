import epicbox

epicbox.configure(
    profiles=[
        epicbox.Profile('python', 'jupyter/scipy-notebook')
    ]
)
files = [{'name': 'main.py', 'content': b'import matplotlib.pyplot as plt;print(43)'}]
limits = {'cputime': 1, 'memory': 64}
result = epicbox.run('python', 'python3 --version && python3 main.py', files=files, limits=limits)
print(result)
