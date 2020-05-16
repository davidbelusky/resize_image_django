Info:
- Work only on linux
- Cronjob apply every day at midnight
- Deleting image objects which are older then 14 days and favourite=False


1. Open terminal
2. crontab -e
3. add cronjob below 

first path = path to virtualenv
second path = path to manage.py of project
delete_old_images = command to apply deleting of images

0 0 * * * path_to_virtualenv path_to_manage.py delete_old_images

Example below:
0 0 * * * /home/user/Desktop/env/bin/python3 /home/user/Desktop/resize_image_django/manage.py delete_old_images
