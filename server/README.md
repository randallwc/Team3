# Sky Ranger Danger: Backend Server

# Getting Started

## First things first

You will need to install **_npm_** (node package manager) and **_nodejs_**. Check the **_package.json_** file to see which version to download.

E.g.

```bash
engines: {
    "node": "12.16.3",
    "npm": "6.14.5"
}
```

Go to https://nodejs.org/en/download/ and download the version specified in **_package.json_** to install both NodeJS and npm
I would suggest finding a tutorial or Youtube video online on how to install **_npm_** and **_nodejs_** to see a visual example

## Checking If You Already Have NodeJS and npm

Confirm that NodeJS and npm were installed correctly with the correct version by running:

```bash
node -v
npm -v
```

## Installing all dependencies

If you just cloned this project, you must have NodeJS and NPM installed beforehand, from the base of the repository, run:

```bash
npm install
```

# Getting the required environmental variables

The last step is getting the required environmental variables

Without them, the application won't work fully.

**Ask me for these variables and I will send you the file**

# Adding new packages with **_NPM_**

For the purpose of this project, say we want to install a new module (e.g. express)

Always pass in **_--save_** flag

If the package/module just makes development easier but not necessarily needed to host the application, (like **_nodemon_**) then pass in **_--save-dev_** flag

https://www.youtube.com/watch?v=rv2xcy0u3y8 <- watch this to understand npm versioning

```bash
npm install --save express
npm install --save --save-dev nodemon
```

# Removing packages with **_NPM_**

The same as installing but with **_uninstall_** keyword

```bash
npm uninstall --save express
npm uninstall --save --save-dev nodemon
```

# Working with **_MongoDB_** Database

## Create a directory named "localDB" at the root of the server (not the whole project)

```bash
mkdir localDB
```

then, run the following command to run DB from terminal (USE YOUR OWN PATH)

```bash
sudo mongod --dbpath <absolute_path_you_chose>
```

## For example, my command is:

```bash
sudo mongod --dbpath /Users/jcrios/Documents/School/ECE180/UCLASeniorProject/Team3/server/localDB
```

> Feel free to make an alias, thats what I did

# Troubleshooting

If having trouble starting up database, sometimes it just has leftover ports it is still using from previous execution. Try:

```bash
sudo killall mongod
```
