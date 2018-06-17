def common(request):
	ctx = {
	'user_id':request.user.id
	}
	return ctx