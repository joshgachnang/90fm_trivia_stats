# file: /etc/nginx/sites-available/yourdomain.com
# nginx configuration for yourdomain.com

server {
        server_name triviastats.com;
        rewrite ^(.*) http://www.triviastats.com$1 permanent;
}

server {
        server_name localhost www.triviastats.com;
        access_log /home/triviastats/90fm_trivia_stats/logs/access.log;
        error_log /home/triviastats/90fm_trivia_stats/logs/error.log;
        listen 80 default_server;
        location / {
                uwsgi_pass unix:/var/run/triviastats/trivia_stats.sock;
#               uwsgi_pass 127.0.0.1:3031;
                include /etc/nginx/uwsgi_params;
        }

        location /static/admin {
                alias /usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin;
                expires max;
                add_header Cache-Control public;
        }
        location /static {
                alias /home/triviastats/90fm_trivia_stats/trivia_stats/static;
        }
}

