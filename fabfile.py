from fabric.api import lcd, local

def prepare_deployment(branch_name):
    local('python manage.py test pm')
    local('git add -p && git commit')

def deploy():
    with lcd('/var/www/vhosts/wpeopm.wpengine.com'):

        local('git pull origin master')
        
        local('python manage.py migrate projects')
        local('python manage.py test projects')
        local('sudo service apache2 restart')

