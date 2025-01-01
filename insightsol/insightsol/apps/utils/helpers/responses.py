from rest_framework.response import Response

def SuccessResponse(response, status=None):

	"""
    @summary: Success response is a utility function to output the final JSON response


    @param res: dict
    @return: Response object

    """

	response_dict = {}
	response_dict['result'] =  True
	response_dict['data'] = response

	#return Success Response
	return Response(response_dict, status=status)

def UnauthorizedResponse():

	"""
    @summary: Unauthorized response is a utility function to output the final JSON response
            when user is not authentciated

    @param status: int
    @return: Response object
    """

	response_dict = {}
	response_dict['status'] = 'unauthorized'

	#return Unauthorized Response
	return Response(response_dict)

def ErrorResponse(message, status=None):

	"""
    @summary: Error response is a utility function to output the final JSON response
            when we need send error message

    @param res: message
    @param status: int
    @return: Response object
    """

	response_dict = {}
	response_dict['status'] = 'error'
	response_dict['message'] = message

	#return Error Response
	return Response(response_dict, status=status)