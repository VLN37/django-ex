# What is this?

This is intended as an **unofficial** Django extension package that adds support
to a few HTMX functionalities. By default, Django ignores request parsing for
all methods that are not GET and POST, this middleware extends that behaviour
to PATCH and PUT HTMX ajax requests.

Since it simulates existing django infrastructure, you should be able to use
and rely on the usual Django request behaviour the same way you do in vanilla,
only with automatically parsed request bodies for those aditional methods.

Your vanilla Django views now work with aditional request methods!

### Who is this for?

You already use HTMX and wants aditional request method flexibility.

### Who is this not for?

Your project uses REST apis or require robust content-type support which would
be better served by standalone packages such as Django Rest Framework.

### How do i use it?

You should be used to acessing data in request.POST. The aditional methods
follow in similar fashion, request.PATCH and request.PUT.

Data is also unifiably available in request.data, regardless of request method.

### Tips

One of the caveats is with the security CRSF token.
You need to explicitly request HTMX to pass the token as a request header.

In your templates you are likely used to doing something like this:

```django
<form hx-post="/route">
    {% csrf token %}
    <-- rest of your form -->
</form>
```

For aditional HTTP methods to work you need to pass it as such:

```django
<form hx-patch="/route" hx-headers="{{csrf token}}">
    <-- rest of your form -->
</form>
```

Since the HX-headers attribute is inherited by nested HTML elements
it is also possible to define it in a base template:

```django
<body hx-headers="{{csrf token}}">
    <form hx-patch="/route">
        <-- rest of your form -->
    </form>
    <-- rest of your page -->
</body>
```

## Installation guide

```py
# download the package
python3 -m pip install django-x

# in your projects settings.py include at the end:
...
MIDDLEWARE = [
    ...
    "django_x.middlewares.http.ProtocolExtensionMiddleware",
]
...
```
