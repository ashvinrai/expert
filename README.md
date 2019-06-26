# Expert

This is a short CLI that allows you to get the top 3 contributers for a git repository

## Usage

```

pip install -r requirements.txt

python3 -m expert path_to_repo

positional arguments:
  path                  the path of the directory to score relative to the
                        root of the project

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         returns all the information used to score the
                        contributers
  -c COMPARE, --compare COMPARE
                        compares the requested directory commits to the
                        commits for the passed in file path
  -r REPO, --repo REPO  path to the desired repo

```

## Scoring Algorithm

The scoring algorithm is very rudimentary. It places a heavy emphasis on number of lines written

```
line_score = num_of_code_lines_written + .2*(num_of_comment_lines_written - num_of_todo_lines_written)

line_score = line_score * (abs(num_of_std_from_avg_time) + 1)

line_score = line_score * (abs(num_of_std_from_avg_num_commits) + 1)

line_score = line_score * (abs(num_of_std_from_avg_num_lines_in_comparison) + 1) if compare_to_directory

```

## Expanding

To expand the scoring algorithm simply extend the implementation of the Expert class and override the `generateScore` method

All of the properties used to generate the base score are available on `Expert().out`

You can call `super().score()` to call the original scoring algorithm

```

from expert.expert import Expert

class newExpert(Expert):
    def generateScore():
        super().generateScore()

        # Do more stuff here

```