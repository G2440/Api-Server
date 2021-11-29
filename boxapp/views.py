from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from boxapp.models import Profile, Store, Box
from .serializers import BoxSerializer1, BoxSerializer2
from django.contrib.auth.models import User
from .signals import createProfile
import datetime
import jwt
from .filters import BoxFilter1,BoxFilter2
from .utils import authenticate,A1,V1,L1,L2

# To create a new user
@api_view(["POST"])
def registerUser(request):
    try:
        user = User.objects.create_user(request.data["username"], request.data["email"], request.data["password"])
        user.save()
        content={"message": "User Created Successfully"}
        return JsonResponse(content,status=200)
    except:
        content={"message": "Error!"}    
        return JsonResponse(content,status=400)

# To log in a new user
@api_view(["POST"])
def loginUser(request):
    user = User.objects.get(username=request.data['username'])
    if user is None:
        content={"message": "Authentication failed"}    
        return JsonResponse(content,status=401)
    if not user.check_password(request.data['password']):
        content={"message": "Authentication failed"}    
        return JsonResponse(content,status=401)
    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=3600),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')
    response = JsonResponse({
        'jwt': token
    })
    return response   

# To get all the boxes
@api_view(["GET"])
def allBoxes(request): 
    token=request.META['HTTP_AUTHORIZATION'].split(' ')[1]
    if(authenticate(token)):
        payload=jwt.decode(token, 'secret', algorithm=['HS256'])
        user = User.objects.get(id=payload['id'])
        profile = Profile.objects.get(user=user)
        if(profile.is_staff):
            filter=BoxFilter2(request.GET,queryset=Box.objects.all())
            serializer = BoxSerializer1(filter.qs,many=True)
            return JsonResponse(serializer.data,safe=False)
        else:
            filter=BoxFilter1(request.GET,queryset=Box.objects.all())
            serializer = BoxSerializer2(filter.qs,many=True)
            return JsonResponse(serializer.data,safe=False)
    else:
        content={"message": "Not authenticated"}    
        return JsonResponse(content,status=401)   

# To get all boxes created by a user
@api_view(["GET"])
def myBoxes(request): 
    token=request.META['HTTP_AUTHORIZATION'].split(' ')[1]
    if(authenticate(token)):
        payload=jwt.decode(token, 'secret', algorithm=['HS256'])
        user = User.objects.get(id=payload['id'])
        profile = Profile.objects.get(user=user)
        if(profile.is_staff):
            filter=BoxFilter1(request.GET,queryset=Box.objects.filter(creator=profile))
            serializer = BoxSerializer1(filter.qs,many=True)
            return JsonResponse(serializer.data,safe=False)
        else:
            content={"message": "Only staff members can view his/her boxes"}
            return JsonResponse(content,status=401)
    else:
        content={"message": "Not authenticated"}    
        return JsonResponse(content,status=401)   

# To add a box 
@api_view(["POST"])
def addBox(request):
    token=request.META['HTTP_AUTHORIZATION'].split(' ')[1]
    if(authenticate(token)):
        try:
            length = request.data['length']
            breadth = request.data['breadth']
            height = request.data['height']
            area = length*breadth
            volume = area*height
            store = Store.objects.get(name="MainStore")
            if((store.current_total_area+area)/(store.total_boxes+1)<=A1):
                payload=jwt.decode(token, 'secret', algorithm=['HS256'])
                user = User.objects.get(id=payload['id'])
                profile = Profile.objects.get(user=user)
                boxes= Box.objects.filter(creator=profile)
                total_volume=0
                for box in boxes:
                    total_volume+=box.volume
                if((total_volume+volume)/(len(boxes)+1)<=V1):
                    last_week=datetime.datetime.now() - datetime.timedelta(days=7)
                    boxes=Box.objects.filter(created__gte=last_week)
                    if(len(boxes)+1<=L1):
                        boxes= Box.objects.filter(creator=profile).filter(created__gte=last_week)
                        if(len(boxes)+1<=L2):
                            if(profile.is_staff):
                                data = {
                                    "creator": profile.id,
                                    "length": length,
                                    "breadth": breadth,
                                    "height": height,
                                    "area": area,
                                    "volume": volume
                                }
                                serializer=BoxSerializer1(data=data)
                                if serializer.is_valid():
                                    serializer.save()
                                    return JsonResponse({"message": "Added Successfully"})
                                store.current_total_area+=area
                                store.total_boxes+=1
                                store.save()
                            else:
                                content={"message": "Only Staff is allowed to add boxes"}
                                return JsonResponse(content,status=401)       
                        else:
                            content={"message": "User Week Limit Exceeded"}
                            return JsonResponse(content,status=400)      
                    else:
                         content={"message": "Week Limit Exceeded"}
                         return JsonResponse(content,status=400)   
                else:
                    content={"message": "Average Volume Limit Exceeded"}
                    return JsonResponse(content,status=400)        
            else:
                content={"message": "Average Area Limit Exceeded"}
                return JsonResponse(content,status=400)
        except:
            content={"message": "Insufficient data"}    
            return JsonResponse(content,status=400)
    else:
        content={"message": "Not authenticated"}    
        return JsonResponse(content,status=401)    

# To update or delete a box depending upon the type of HTTP request
class BoxClass(APIView):

    def put(self,request,pk):
        token=request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        if(authenticate(token)):
            try:
                length = request.data['length']
                breadth = request.data['breadth']
                height = request.data['height']
                area = length*breadth
                volume = area*height
                store = Store.objects.get(name="MainStore")
                try:
                    box = Box.objects.get(id=pk)
                    cta=store.current_total_area
                    cta-=box.area
                    cta+=area
                    if(cta/(store.total_boxes)<=A1):
                        payload=jwt.decode(token, 'secret', algorithm=['HS256'])
                        user = User.objects.get(id=payload['id'])
                        profile = Profile.objects.get(user=user)
                        boxes= Box.objects.filter(creator=profile)
                        total_volume=0
                        for box in boxes:
                            total_volume+=box.volume
                        box = Box.objects.get(id=pk)
                        total_volume-=box.volume
                        total_volume+=volume
                        if((total_volume)/(len(boxes))<=V1):
                            if(profile.is_staff):
                                store.current_total_area-=box.area
                                store.current_total_area+=area
                                store.save()
                                data = {
                                    "length": length,
                                    "breadth": breadth,
                                    "height": height,
                                    "area": area,
                                    "volume": volume,
                                    "updated": datetime.datetime.now()
                                }
                                serializer=BoxSerializer1(box,data=data)
                                if serializer.is_valid():
                                    serializer.save()
                                    return JsonResponse({"message": "Box updated successfully"})
                            else:
                                content={"message": "Only Staff is allowed to add boxes"}
                                return JsonResponse(content,status=401)    
                        else:
                            content={"message": "Average Volume Limit Exceeded"}
                            return JsonResponse(content,status=400)
                    else:
                        content={"message": "Average Area Limit Exceeded"}
                        return JsonResponse(content,status=400)
                except:
                    content={"message": "Box with given id does not exist"}    
                    return JsonResponse(content,status=400)
            except:
                content={"message": "Insufficient data"}    
                return JsonResponse(content,status=400)
        else:
            content={"message": "Not authenticated"}    
            return JsonResponse(content,status=401)

    def delete(self,request,pk):
        token=request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        if(authenticate(token)):
            try:
                box = Box.objects.get(id=pk)
                payload=jwt.decode(token, 'secret', algorithm=['HS256'])
                user = User.objects.get(id=payload['id'])
                profile = Profile.objects.get(user=user)
                if(box.creator==profile):
                    box=Box.objects.get(id=pk)
                    store=Store.objects.get(name="MainStore")
                    store.current_total_area-=box.area
                    store.total_boxes-=1
                    boxes= Box.objects.filter(creator=profile)
                    total_volume=0
                    for b in boxes:
                        total_volume+=b.volume
                    total_volume-=box.area
                    if(store.current_total_area/store.total_boxes<=A1 and total_volume/store.total_boxes<=V1):
                        store.save()
                        box.delete()
                        return JsonResponse({"message": "Box deleted successfully"})
                    else:
                        content={"message": "Average Area/Volume Limit Exceeded"}
                        return JsonResponse(content,status=401)
                else:
                    content={"message": "Only creator can delete the box"}    
                    return JsonResponse(content,status=401)    
            except:
                content={"message": "Box with given id does not exist"}    
                return JsonResponse(content,status=400)
        else:
            content={"message": "Not authenticated"}    
            return JsonResponse(content,status=401)