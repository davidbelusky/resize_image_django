# Resize and style images  <br/>Django rest API

Rest API created in django rest framework for uploading images which can be resized or stylized by using AI style transfer.

## Info:

* Features: 
     * Register users
     * Upload and resize images
     * Upload and styling images with custom styles by using AI style transfer model
     * Share resized and styled images with other users
     * Mark images as favourite
     * Cronjob once per day at midnight delete images which are older then 14 days and not marked as favourite
* Created and tested on:
     * Ubuntu 20.04
     * Python 3.8.2
     * Tensorflow 2.2.0

## Requirements:

- Ubuntu 20.04 or higher
- Python 3.8.2 or higher

## Startup:

1. Install pip 
   ``` sudo apt-get install python3-pip ```
2. Install virtualenv
   ```sudo pip3 install virtualenv```
3. Create and activate virtual environment
   create:  ```virtualenv env```
   activate:  ```source env/bin/activate```
4. Install requirements
   ```pip3 install -r requirements.txt```
5. Navigate to django project 'resize_image_django' and input below code to start server
   ```python3 manage.py runserver```
6.  To run test
   ```python3 manage.py test```

#### Cronjob tutorial:
##### Info:
Cronjob start every day at midnight.
Command 'delete_old_images'  delete all images and styled images which are older then 14 days and favourite = False

 1. Open terminal

 2. ```crontab -e```

 3. add cronjob below
    ```0 0 * * * path_to_virtualenv path_to_manage.py delete_old_images```

    example - ```0 0 * * * /home/user/Desktop/env/bin/python3 /home/user/Desktop/resize_image_django/manage.py delete_old_images```

#### Docker tutorial:

1. Edit 'DATABASES' in django project settings.py as below (mysite/settings.py):

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'django',
           'USER': 'david',
           'PASSWORD': 'dav',
           'HOST': 'db',
           'PORT': 5432,
       }
   }
   ```

2.  In django project folder run command below to build docker image:

   ```docker-compose build```

3.  After build docker image, we can run builded image:

   ```docker-compose up```

## Endpoints

### Register new user:

#### Info:

**Endpoint:** /api-auth/register/

**Allowed methods:** [POST]

#### Fields:

**_username_** - must be unique, allowed letters, digits and @/./+/-/_ only

**_email_** - email of user 

**_password_** - min. length = 5, cannot be common



**POST** `/api-auth/register/`

```json 
{
    "username": "david",
    "email": "david@email.com",
    "password":"test123",
    "password2":"test123"
}
```

##### Response: created user object

```json 
{
  "username": "david",
  "email": "david@email.com"
}
```

### Upload and resize new image:

#### Info:

**Endpoint:** `/images/`

**Allowed methods:** [GET,POST]

**Filters:** [id, img_name, img_description, img_format, favourite, created_date]

**Search filter**: ['img_name'] 

Upload and resize image for logged user.

#### Fields:

**_owner_** - username of user who upload image. **read_only=True**

**_img_name_** - unique name of image. Max allowed length 25 chars. **required=True**

**_img_description_** - textfield for description of image. Max allowed length 250 chars.

**_created_date_** - datetime when image was uploaded. **read_only=True**

**_img_format_** - format of image automatically get from uploaded_image. **read_only=True**

**_favourite_** - boolean, default = false

**_uploaded_image_** - path to image for upload. **required=True**

**_width_** - width of image. If blank set original width of uploaded image. Max allowed width is 1920. If input is > 1920 automatically set to 1920 pixels

**_height_** - height of image. Same rules as for width only difference is that max allowed height is 1080

**_share_user_** - ID of registered user who will be able to see uploaded image. In share_user is not allowed to input id of owner image



Requires user authorization

**POST** `/images/`

```json
{
    "img_name":"my_picture",
    "img_description":"my first picture",
    "uploaded_image":"/pic.jpg",
    "favourite":true,
    "width":800,
    "height":500,
    "share_user":2
}
```

##### Response: created image object

```json 
{
    "id": 1,
    "img_format": "jpg",
    "owner": "david",
    "img_name": "my_picture",
    "img_description": "my first picture",
    "created_date": "2020-05-17T11:05:19.910033Z",
    "favourite": true,
    "uploaded_image": "http://127.0.0.1:8000/media/pics/owner_1/pic.jpg",
    "width": 800,
    "height": 500,
    "share_user": [
        2
    ]
}
```

**GET** `/images/`

##### Response: All image objects for logged user

```json 
[    
	{
        "id": 1,
        "img_format": "jpg",
        "owner": "david",
        "img_name": "my_picture",
        "img_description": "my first picture",
        "created_date": "2020-05-17T11:05:19.910033Z",
        "favourite": true,
        "uploaded_image": "http://127.0.0.1:8000/media/pics/owner_1/pic.jpg",
        "width": 800,
        "height": 500,
        "share_user": [
            2
        ]
    },
    {
        "id": 2,
        "img_format": "jpg",
        "owner": "david",
        "img_name": "second_image",
        "img_description": "my second image",
        "created_date": "2020-05-17T11:12:31.863448Z",
        "favourite": false,
        "uploaded_image": "http://127.0.0.1:8000/media/pics/owner_1/style.jpg",
        "width": 700,
        "height": 490,
        "share_user": [
            2,
            3
        ]
    }
]
```



### Edit or delete image object:

#### Info:

**Endpoint:** `/images/<int:pk>`

**Allowed methods:** [GET,PUT,DELETE]

Edit or delete image object.

#### Fields:

Same fields as during posting new image only field 'uploaded_image' is excluded.

**Editable fields:** img_name,img_description,favourite,width,height,share_user 

**PUT** `/images/1`

```json
{
    "img_name":"my_picture_edited",
    "img_description":"my first picture with edited content",
    "favourite":false,
    "width":3000,
    "height":5000,
    "share_user":2
}
```

##### Response: edited image object

```json 
{
    "id": 1,
    "owner": "david",
    "img_name": "my_picture_edited",
    "img_description": "my first picture with edited content",
    "img_format": "jpg",
    "created_date": "2020-05-17T11:05:19.910033Z",
    "favourite": false,
    "uploaded_image": "http://127.0.0.1:8000/media/pics/owner_3/pic_bP2uPGS.jpg",
    "width": 1920,
    "height": 1080,
    "share_user": [
        2
    ]
}
```

**GET**`/images/1`

**Response:** object with inputted PK

```json 
{
    "id": 1,
    "owner": "david",
    "img_name": "my_picture_edited",
    "img_description": "my first picture with edited content",
    "img_format": "jpg",
    "created_date": "2020-05-17T11:05:19.910033Z",
    "favourite": false,
    "uploaded_image": "http://127.0.0.1:8000/media/pics/owner_3/pic_bP2uPGS.jpg",
    "width": 1920,
    "height": 1080,
    "share_user": [
        2
    ]
}
```

**DELETE**`/images/1`

**Response:** HTTP 204 No content



### Upload styled image:

#### Info:

**Endpoint:** `/styled_images/`

**Allowed methods:** [GET,POST]

**Filters:** [id, img_name, img_description, img_format, favourite, created_date]

**Search filter**: ['img_name'] 

Use AI style transfer to style selected original image, owner of selected original image must be logged user. User can upload own style image which will be apply to stylizing original image.

#### Image stylizing example:
**Original image:**

![Original_image](https://raw.githubusercontent.com/davidbelusky/resize_image_django/master/styled_image_example/img.jpg)

**Style image:**

![Style image](https://github.com/davidbelusky/resize_image_django/blob/master/styled_image_example/style.jpeg)

**Styled image:**

![Styled image](https://github.com/davidbelusky/resize_image_django/blob/master/styled_image_example/styled_image.jpeg)


#### Fields:

**_owner_** - username of user who upload styled image. **read_only=True**

**_img_name_** - unique name of styled image. Max allowed length 25 chars. **required=True**

**_img_description_** - textfield for description of image. Max allowed length 250 chars.

**_created_date_** - datetime when image was uploaded. **read_only=True**

**_favourite_** - boolean, default = False

**_original_image_** -  ID of image object to which it is to be applied style transfer. Logged user must be owner of selected original_image. **required=True**

**_styled_image_** - path to style which would be applied to original image. **required=True**

**_share_user_** - ID of registered user who will be able to see uploaded image. In share_user is not allowed to input id of owner image



Requires user authorization

**POST** `/styled_images/`

```json
{
    "img_name":"my_styled_pic",
    "img_description":"my first styled picture",
    "uploaded_image":"/style.jpg",
    "favourite":true,
    "original_image": 1,
    "share_user":2
}
```

##### Response: created styled image object

```json 
{
    "id": 1,
    "owner": "david",
    "img_name": "my_styled_pic",
    "styled_image": "http://127.0.0.1:8000/media/pics/owner_1/styled_images/style.jpg",
    "img_description": "my first styled picture",
    "img_format": "jpg",
    "created_date": "2020-05-17T14:50:22.387527Z",
    "favourite": false,
    "original_image": 1,
    "share_user": [
        2
    ]
}
```

**GET** `/styled_images/`

**Response:** List of all styled image objects where owner is logged user

```json 
{
    "id": 1,
    "owner": "david",
    "img_name": "my_styled_pic",
    "styled_image": "http://127.0.0.1:8000/media/pics/owner_1/styled_images/style.jpg",
    "img_description": "my first styled picture",
    "img_format": "jpg",
    "created_date": "2020-05-17T14:50:22.387527Z",
    "favourite": false,
    "original_image": 1,
    "share_user": [    
  		2
    ]
}
```

### Edit or delete styled image object:

#### Info:

**Endpoint:** `/styled_image/<int:pk>`

**Allowed methods:** [GET,PUT,DELETE]

Edit or delete styled image object.

#### Fields:

Same fields as during posting new styled image only fields 'original_image' and 'style_image' is excluded.

**Editable fields:** img_name,img_description,favourite,share_user 

**PUT** `/images/1`

```json
{
    "img_name":"my_styled_picture_edited",
    "img_description":"my first styled picture with edited content",
    "favourite":true,
    "share_user":2
}
```

##### Response: edited image object

```json 
{
    "id": 1,
    "owner": "david",
    "img_name": "my_styled_picture_edited",
    "styled_image": "http://127.0.0.1:8000/media/pics/owner_1/styled_images/style.jpg",
    "img_description": "my first styled picture with edited content",
    "img_format": "jpg",
    "created_date": "2020-05-17T14:50:22.387527Z",
    "favourite": true,
    "original_image": 1,
    "share_user": [
        2
    ]
}
```

**GET**`/images/1`

**Response:** object with inputted PK

```json 
{
    "id": 1,
    "owner": "david",
    "img_name": "my_styled_picture_edited",
    "styled_image": "http://127.0.0.1:8000/media/pics/owner_1/styled_images/style.jpg",
    "img_description": "my first styled picture with edited content",
    "img_format": "jpg",
    "created_date": "2020-05-17T14:50:22.387527Z",
    "favourite": true,
    "original_image": 1,
    "share_user": [
        2
    ]
}
```

**DELETE**`/images/1`

**Response:** HTTP 204 No content



### Show shared images

#### Info:

**Endpoint:** `/shared_images/`

**Allowed methods:** [GET]

Show all images and styled images which other users share with logged user

**GET**`/shared_images/`

**Response:** shared image objects with logged user

```json 
{
    "images": [
        {
            "id": 5,
            "img_format": "jpg",
            "owner": "patrik",
            "img_name": "patrik_first_image",
            "img_description": "",
            "created_date": "2020-05-17T15:01:36.477046Z",
            "favourite": false,
            "uploaded_image": "http://127.0.0.1:8000/media/pics/owner_4/pic.jpg",
            "width": 500,
            "height": 477,
            "share_user": [
                1
            ]
        }
    ],
    "styled_images": [
        {
            "id": 3,
            "owner": "patrik",
            "img_name": "patrik_styled_image",
            "styled_image": "http://127.0.0.1:8000/media/pics/owner_4/styled_images/style.jpg",
            "img_description": "",
            "img_format": "jpg",
            "created_date": "2020-05-17T15:02:12.434944Z",
            "favourite": false,
            "original_image": 5,
            "share_user": [
                1
            ]
        },
        {
            "id": 4,
            "owner": "karol",
            "img_name": "karol_styled_first_image",
            "styled_image": "http://127.0.0.1:8000/media/pics/owner_5/styled_images/style.jpg",
            "img_description": "",
            "img_format": "jpg",
            "created_date": "2020-05-17T15:03:06.761047Z",
            "favourite": false,
            "original_image": 6,
            "share_user": [
                1
            ]
        }
    ]
}
```

### Show favourite images

#### Info:

**Endpoint:** `/favourites/`

**Allowed methods:** [GET]

Show all images and styled images which have set favourite field to True and owner is logged user.

**GET**`/favourites/`

**Response:** favourite image objects which owner is logged user

```json 
{
    "images": [
        {
            "id": 3,
            "img_format": "jpg",
            "owner": "david",
            "img_name": "my_picture_edited",
            "img_description": "my first picture with edited content",
            "created_date": "2020-05-17T11:05:19.910033Z",
            "favourite": true,
            "uploaded_image": "http://127.0.0.1:8000/media/pics/owner_1/pic_bP2uPGS.jpg",
            "width": 1920,
            "height": 1080,
            "share_user": [
                2
            ]
        },
        {
            "id": 4,
            "img_format": "jpg",
            "owner": "david",
            "img_name": "second_image",
            "img_description": "my second image",
            "created_date": "2020-05-17T11:12:31.863448Z",
            "favourite": true,
            "uploaded_image": "http://127.0.0.1:8000/media/pics/owner_1/style.jpg",
            "width": 700,
            "height": 490,
            "share_user": [
                1,
                2
            ]
        }
    ],
    "styled_images": [
        {
            "id": 2,
            "owner": "david",
            "img_name": "styled",
            "styled_image": "http://127.0.0.1:8000/media/pics/owner_1/styled_images/style.jpg",
            "img_description": "my first styled picture",
            "img_format": "jpg",
            "created_date": "2020-05-17T14:59:25.001582Z",
            "favourite": true,
            "original_image": 4,
            "share_user": [
                2
            ]
        }
    ]
}
```

### 



