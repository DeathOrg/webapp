# webapp

- **Commands to set up git remotes:**

  ```bash
    git remote | xargs -n 1 git remote remove (To remove all remotes)
    git remote remove origin (To remove specific remote, in this case origin)
    git remote add sourabh git@github.com:Sourabh-Kumar7/webapp.git
    git remote add upstream git@github.com:DeathOrg/webapp.git
    git remote set-url --push upstream no_push