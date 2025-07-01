#version 330

in vec2 v_vTexCoord;
out vec4 fragColor;

uniform float time;
uniform vec2 resolution;

void main()
{
    vec2 uv = gl_FragCoord.xy / resolution.xy;
    float r = 0.5 + 0.5 * cos(time + uv.xyx + vec3(0.0, 2.0, 4.0));
    fragColor = vec4(r, 1.0);
}
