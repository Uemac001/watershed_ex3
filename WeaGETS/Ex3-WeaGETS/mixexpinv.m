function x = mixexpinv(Px,p,mu1,mu2)
% Inverse CDF of the mixed exponential distribution.
% The CDF is F(x) = 1 - p*exp(-x/mu1) - (1-p)*exp(-x/mu2), increasing for x >= 0.
% The root is searched in the bracket [0, xu] with xu slightly above
% -max(mu1,mu2)*log(1-Px), where F(xu) >= Px. (The original code started fzero from a random point; when a
% fit degenerates, e.g. p = 0 with a tiny mu1, fzero searched negative x, hit
% exp(...) = Inf and returned NaN.)
objfun=@(x,Par) Par(1)-1+Par(2)*exp(-x/Par(3))+(1-Par(2))*exp(-x/Par(4));
Px=Px(:);
n=length(Px);
options=optimset('MaxIter',10000,'TolFun',1e-10,'TolX',1e-10);
x=zeros(n,1);
mumax=max(mu1,mu2);
for i=1:n
    Pi=min(Px(i),1-eps);
    if Pi<=0
        x(i)=0;
        continue
    end
    Par=[Pi p mu1 mu2];
    xu=-mumax*log(1-Pi)*1.01+1e-6;   % small margin: F(xu) can equal Px up to rounding
    x(i)=fzero(objfun,[0 xu],options,Par);
end
end
