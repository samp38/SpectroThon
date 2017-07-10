% Merci Quentin !!

indices = 0:4;

% myStruct = cell( size( indices ) );
myStruct = struct();

for i = 1:numel( indices )
    
    name = [ 'pcaDistances_xSmooth_', num2str(indices(i)) ];
    myStruct.(name) = load( [ name, '.mat' ] );
    
end


% le super plot

fields = fieldnames( myStruct );

f = figure(1);
clf
hold on
grid on

for i = 1:numel( fields )
    
    plot( myStruct.(fields{i}).Db );
    set( gca, 'YScale', 'log' );
    
end
legend(fields)

% set X labels

xticks( 1:numel( myStruct.(fields{1}).Db ) );
xticklabels( myStruct.(fields{1}).pair );
set(gca,'XTickLabelRotation',45)