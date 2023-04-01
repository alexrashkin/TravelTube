from django import forms

from .models import Post, Comment, Image


class PostForm(forms.ModelForm):
    images = forms.ImageField(widget=forms.ClearableFileInput(
        attrs={'multiple': True}), required=False)

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data.get('text')
        if data is None:
            raise forms.ValidationError('Поле не заполнено')
        return data

    def save(self, commit=True):
        post = super().save(commit=False)
        images = self.cleaned_data.get('images')

        if commit:
            post.save()

            if images:

                for image in images:
                    Image.objects.create(image=image, post=post)

        return post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
