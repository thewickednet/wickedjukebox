from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django_countries.fields import CountryField
from sorl.thumbnail import ImageField


class MyUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class Artist(models.Model):
    name = models.CharField(max_length=128)
    country = CountryField(null=True, blank=True)
    bio = models.TextField()
    website = models.URLField(max_length=255, blank=True, null=True)
    wikipage = models.URLField(max_length=255, blank=True, null=True)
    lastfm_mbid = models.CharField(max_length=64)
    photo = ImageField(max_length=255, null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name is not None:
            return self.name
        return ""

    class Meta:
        ordering = ["name"]


class Album(models.Model):
    class AlbumChoices(models.TextChoices):
        album = "Album"
        ost = "Movie Soundtrack"
        game = "Game Soundtrack"
        various = "Various Artists"

    artist = models.ForeignKey(
        Artist, related_name="albums", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=128)
    release_date = models.DateField()
    added = models.DateTimeField(auto_now_add=True)
    downloaded = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=32, choices=AlbumChoices.choices)
    path = models.CharField(max_length=255)
    coverart = ImageField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.name is not None:
            return self.name
        return ""

    class Meta:
        ordering = ["-release_date", "name"]


class Song(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(
        Album,
        blank=True,
        null=True,
        related_name="songs",
        on_delete=models.CASCADE,
    )
    track_no = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=128)
    duration = models.FloatField(null=True, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    localpath = models.CharField(max_length=255)
    downloaded = models.PositiveIntegerField(default=0)
    lastScanned = models.DateTimeField(null=True, blank=True)
    bitrate = models.IntegerField(default=0)
    filesize = models.PositiveBigIntegerField(default=0)
    checksum = models.CharField(max_length=14)
    lyrics = models.TextField()
    broken = models.BooleanField(default=False)
    dirty = models.BooleanField(default=False)
    added = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)

    def duration_int(self):
        return int(self.duration)

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

    class Meta:
        ordering = ["album", "track_no"]


class Channel(models.Model):
    name = models.SlugField(unique=True, max_length=32)
    public = models.BooleanField(default=True)
    backend = models.CharField(max_length=64)
    backend_params = models.TextField(blank=True, null=True)
    ping = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True)
    status = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class ChannelSongData(models.Model):
    channel = models.OneToOneField(Channel, on_delete=models.CASCADE)
    song = models.ForeignKey("Song", on_delete=models.CASCADE)
    played = models.PositiveIntegerField(default=0)
    voted = models.PositiveIntegerField(default=0)
    skipped = models.PositiveIntegerField(default=0)
    last_played = models.DateTimeField(blank=True, null=True)
    cost = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (("channel", "song"),)


class DynamicPlaylist(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    probability = models.FloatField()
    label = models.CharField(max_length=64, blank=True, null=True)
    query = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.label


class Event(models.Model):
    title = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.title


class Playlist(models.Model):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="playlists"
    )
    name = models.CharField(max_length=32)
    probability = models.FloatField(blank=True, null=True)


class PlaylistSong(models.Model):
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, related_name="songs"
    )
    song = models.ForeignKey("Song", on_delete=models.CASCADE)
    position = models.IntegerField()

    class Meta:
        unique_together = (("playlist", "song"),)


class Queue(models.Model):
    song = models.ForeignKey("Song", models.PROTECT)
    user = models.ForeignKey("User", models.PROTECT, blank=True, null=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    position = models.IntegerField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["channel", "position"]

    def __str__(self):
        if self.song is not None:
            return self.song.title
        return ""


class RenderPresets(models.Model):
    category = models.CharField(max_length=64)
    preset = models.CharField(max_length=64)
    h_max = models.SmallIntegerField()
    w_max = models.SmallIntegerField()
    placeholder = models.CharField(max_length=64, blank=True, null=True)
    no_proportion = models.IntegerField()
    force_mime = models.CharField(max_length=10)


class Setting(models.Model):
    var = models.CharField(max_length=32)
    value = models.TextField(blank=True, null=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    class Meta:
        unique_together = (("var", "channel", "user"),)


class UserAlbumStats(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "album", "when"),)


class UserSongStanding(models.Model):
    class StandingChoices(models.TextChoices):
        love = "Love"
        hate = "Hate"

    user = models.OneToOneField("User", on_delete=models.CASCADE)
    song = models.OneToOneField(Song, on_delete=models.CASCADE)
    standing = models.CharField(max_length=4, choices=StandingChoices.choices)
    inserted = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("user", "song"),)

    def __str__(self):
        return f"{self.user} - {self.song}"


class UserSongStats(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)
    song = models.OneToOneField(Song, on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "song", "when"),)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=32)
    fullname = models.CharField(max_length=64)
    email = models.CharField(max_length=128)
    credits = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    votes = models.IntegerField(default=0)
    skips = models.IntegerField(default=0)
    selects = models.IntegerField(default=0)
    added = models.DateTimeField(auto_now_add=True)
    proof_of_life = models.DateTimeField(blank=True, null=True)
    proof_of_listening = models.DateTimeField(blank=True, null=True)
    ip = models.GenericIPAddressField(
        blank=True, null=True, verbose_name="IP", help_text="Last IP Address"
    )
    picture = ImageField(blank=True, null=True)
    channel = models.ForeignKey(
        Channel,
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    pinned_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="Pinned IP",
        help_text="fake the User's IP",
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_staff = models.BooleanField(default=True, verbose_name="Staff")

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["fullname"]

    def __str__(self):
        return self.fullname
