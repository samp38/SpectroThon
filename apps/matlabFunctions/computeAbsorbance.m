rootDir = '/Users/sam/Documents/IDV/projects/SpectroThon/apps/appDatabase/measurements/2017-03-27_drugs.BAK2/';
cd /Users/sam/Documents/IDV/projects/SpectroThon/apps/appDatabase/measurements/2017-03-27_drugs.BAK2/
files = dir('*.mat');
cnt = 0;
for file = files'
    windowSize = 33;
    cnt = cnt + 1;
    load(file.name);
    disp(file.name);
    lambdas = points(:,1);
    dark = conv(points(:,4), ones(1,windowSize), 'same');
    blank = conv(points(:,2), ones(1,windowSize), 'same');
    transmition = conv(points(:,3), ones(1,windowSize), 'same');
    points(:,5) = -log((transmition - dark)./ (blank - dark));
    %plot(lambdas, points(:,5));
    save(file.name,'indice','points','specieKey');
    clear indice
    clear points
    clear specieKey
    clear dark
    clear blank
    clear transmition
    disp(cnt)
end