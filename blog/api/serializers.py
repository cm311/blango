from rest_framework import serializers
from blog.models import Post, Tag, Comment
from blango_auth.models import User

class TagField(serializers.SlugRelatedField):
  def to_internal_Value(self, data):
    try:
      return self.get_queryset().get_or_create(value=data.lower())[0]
    except (TypeError, ValueError):
      self.fail(f"Tag value{data} is invalid")

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ["first_name", "last_name", "email"]

class CommentSerializer(serializers.ModelSerializer):
  id = serializers.IntegerField(required=False)
  creator = UserSerializer(read_only=True)

  class Meta:
    model = Comment
    fields = ["id", "creator", "content", "modifed_at", "created_at"]
    readonly = ["modifed_at", "created_at"]

class PostSerializer(serializers.ModelSerializer):
  tags = serializers.SlugRelatedField(
    slug_field="value", many=True, queryset=Tag.objects.all()
  )

  author = serializers.HyperlinkedRelatedField(
    queryset=User.objects.all(), view_name="api_user_detail", lookup_field="email"
  )

  class Meta:
    model = Post
    fields = "__all__"
    readonly = ["modifed_at", "created_at"]

class PostDetailSerializer(PostSerializer):
  comments = CommentSerializer(many=True)

  def update(self, instance, validated_data):
    comments = validated_data.pop("comments")

    instance = super(PostDetailSerializer, self).update(instance, validated_data)

    for comment_data in comments:
      if comment_data in comments:
        #comment has an ID so it was pre existing
        continue

      comment = Coment(**comment_data)
      comment.creator = self.context["request"].user
      comment.content_object = instance
      comment.save()

    return instance


