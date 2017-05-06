# envs

## Installation

### Requirements

**oh-my-zsh**

```
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
```
> https://github.com/robbyrussell/oh-my-zsh

**homebrew**

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
> https://brew.sh

**pyenv**

```
brew install pyenv
# then add this to ~/.zshrc
if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi
if which pyenv-virtualenv-init > /dev/null; then eval "$(pyenv virtualenv-init -)"; fi
```
> https://github.com/pyenv/pyenv
