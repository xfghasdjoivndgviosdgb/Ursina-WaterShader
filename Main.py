from ursina import *

SpecularShaderV1=Shader(language=Shader.GLSL,vertex="""
#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewMatrix;
uniform sampler2D p3d_Texture0;
uniform mat3 p3d_NormalMatrix;
uniform vec3 lightPos;
uniform vec3 cameraPos;
uniform sampler2D heightMap;
uniform vec2 textureoffset;
uniform sampler2D normalMap;

in vec2 p3d_MultiTexCoord0;
in vec4 vertex;
in vec4 normal;

out vec3 vectorToLight;
out vec3 vectorToCamera;
out vec2 texcoord;
out float alpha;

void main(){
    vec2 coord=p3d_MultiTexCoord0+textureoffset;
    float hgt=texture(heightMap,coord).x*50;

    gl_Position=p3d_ModelViewProjectionMatrix*vec4(vertex.x,vertex.y+hgt,vertex.z,vertex.w);
    vec3 worldPos=(p3d_ModelMatrix*vertex).xyz;
    vectorToLight=lightPos-worldPos;
    vectorToCamera=(inverse(p3d_ViewMatrix)*vec4(0.0,0.0,0.0,1.0)).xyz-worldPos.xyz;
    texcoord=coord*12;
    alpha=hgt/40;
    alpha-=sin(dot(vectorToCamera,vec3(0,1,0)))/180;
    alpha=max(alpha,0.1);
    alpha+=0.1;
}
""",fragment="""
#version 140

uniform vec3 lightColor;
uniform float Damper;
uniform float reflectivity;
uniform sampler2D p3d_Texture0;
uniform sampler2D normalMap;
uniform mat3 p3d_NormalMatrix;

in vec3 vectorToLight;
in vec3 vectorToCamera;
in vec2 texcoord;
in vec3 surfaceNormal;
in float alpha;

out vec4 out_color;

void main(){
    vec3 surfaceNormal=p3d_NormalMatrix*texture(normalMap,texcoord).xyz;
    vec4 col=texture(p3d_Texture0,texcoord);
    vec4 color=vec4(0.0,0.0,col.b,col.a);
    vec3 unitNormal=normalize(surfaceNormal);
    vec3 unitToLight=normalize(vectorToLight);
    vec3 unitToCamera=normalize(vectorToCamera);
    vec3 lightDir=-unitToLight;
    float nDotl=dot(unitNormal,lightDir);
    float brightness=max(nDotl,0.2);
    vec3 diffuse=brightness*lightColor;
    vec3 reflectedLight=reflect(lightDir,unitNormal);
    float specular=dot(reflectedLight,unitToCamera);
    specular=max(specular,0.0);
    float damper=pow(specular,Damper);
    vec3 finalSpecular=damper*reflectivity*lightColor;
    vec4 color_final=vec4(diffuse,1.0)*color+vec4(finalSpecular,1.0);
    out_color=vec4(color_final.xyz,alpha+dot(unitToCamera,surfaceNormal)/5);
}
""")


class water(Entity):
    def __init__(self,height,size):
        super().__init__()
        self.shader=SpecularShaderV1
        self.vertices=list()
        self.triangles=list()
        self.uvs=list()
        self.hgt=height
        self.createMesh(size)
        self.model=Mesh(vertices=self.vertices,triangles=self.triangles,uvs=self.uvs)
        self.set_shader_input("cameraPos",Vec3(0,0,0))
        self.set_shader_input("lightPos",Vec3(3,10,2))


    def createMesh(self,size):
        for x in range(size):
            for z in range(size):
                index=len(self.vertices)

                self.vertices.extend((Vec3(x,self.hgt,z),Vec3(x+1,self.hgt,z),Vec3(x+1,self.hgt,z+1),Vec3(x,self.hgt,z+1)))
                self.triangles.extend(((index,index+1,index+2),(index+0,index+2,index+3)))
                self.uvs.extend(((Vec2(x/size,(z)/size),Vec2((1+x)/size,(z)/size),Vec2((1+x)/size,(z+1)/size),Vec2(x/size,(z+1)/size))))




if __name__=="__main__":
    from ursina import *
    from ursina.prefabs.editor_camera import EditorCamera
    import random
    import math
    light_x=0
    light_y=0
    offset_x=0
    offset_y=0
    def update():
        global light_x
        global light_y
        global offset_x
        global offset_y
        a.set_shader_input("cameraPos",p.position)
        a.set_shader_input("textureoffset",Vec2(offset_x,offset_y))
        offset_x+=0.07*time.dt

    app=Ursina()
    p=EditorCamera()
    a=water(0,300)
    a.set_shader_input("lightPos",Vec3(25,100,25))
    a.set_shader_input("reflectivity",1.0)
    a.set_shader_input("Damper",14.0)
    a.set_shader_input("lightColor",Vec3(1,1,1))
    a.set_shader_input("normalMap",load_texture("water_normalMap"))
    a.set_shader_input("heightMap",load_texture("water_heightMap"))
    app.run()
