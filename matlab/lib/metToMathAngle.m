function [ mathAngle ] = metToMathAngle( metAngle )
%METTOMATHANGLE Convert angles from meteorological convention (in degrees)
%to mathematical convention (in radians)
%   Detailed explanation goes here
    mathAngle = (90-metAngle).*pi./180;
end

