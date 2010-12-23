function I = simprule(d,h,x)
%SIMPRULE Simpson's rule integration.
% I = SIMPRULE(d,h,x) returns the Simpson's rule approximation
% for the integral of the data in d with step size of h, or at the independent
% variable values of x (note; if x is specified, h is ignored)
% d and x can be either row vectors or columns vectors, they just need to
% have agreement in their size.

if nargin<2
    error('Must specify h or x')
end
if nargin==2
    nd = length(d);
    if(nd>=3)
        if(mod(nd,2)==1)
            n = nd;
        else
            n = nd-1;
        end
        I = h/3 * (d(1) + 4*sum(d(2:2:(n-1))) + 2*sum(d(3:2:(n-1))) + d(n));
    else
        n=1;
        I = 0;
    end
    
    if(n+1==nd)
        I = I + h/2*sum(d(n:(n+1)));
    elseif (n+2==nd)
        I = I + h/2*sum([d(n:(n+2)),d(n+1)]);
    end
else
    n = length(d)-1;
    I = sum( (x(2:(n+1))-x(1:n)).*(d(1:n)+d(2:(n+1))) )/2;
end



end