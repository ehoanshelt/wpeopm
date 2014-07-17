from django.forms import widgets

from rest_framework import serializers

from projects.models import Link

class LinkSerializer(serializers.ModelSerializer):
	class Meta:
		model = Link
		fields = ('id', 'name', 'description', 'code', 'project')

	def restore_object(self, attrs, instance=None):
		"""
		Create or update a new Link instance, given a dictionary of
		deserialized field values.
		"""
		if instance:
			# Update existing instance
			instance.name = attrs.get('name', instance.name)
			instance.description = attrs.get('description', instance.description)
			instance.code = attrs.get('code', instance.code)
			instance.project = attrs.get('project', instance.project)