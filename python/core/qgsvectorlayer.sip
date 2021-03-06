
typedef QList<int> QgsAttributeList;
typedef QSet<int> QgsAttributeIds;

/** @note Added in 1.9 */
class QgsAttributeEditorElement : QObject
{
%TypeHeaderCode
#include "qgsvectorlayer.h"
%End

  public:

    enum AttributeEditorType
    {
      AeTypeContainer,
      AeTypeField,
      AeTypeInvalid
    };

    QgsAttributeEditorElement( AttributeEditorType type, QString name, QObject *parent = NULL );

    virtual ~QgsAttributeEditorElement();

    QString name() const;
    AttributeEditorType type() const;

    virtual QDomElement toDomElement( QDomDocument& doc ) const = 0;
};

/** @note Added in 1.9 */
class QgsAttributeEditorContainer : QgsAttributeEditorElement
{
%TypeHeaderCode
#include "qgsvectorlayer.h"
%End

  public:
    QgsAttributeEditorContainer( QString name, QObject *parent );
    ~QgsAttributeEditorContainer();

    virtual QDomElement toDomElement( QDomDocument& doc ) const;
    virtual void addChildElement( QgsAttributeEditorElement *widget );
    QList<QgsAttributeEditorElement*> children() const;
};

/** @note Added in 1.9 */
class QgsAttributeEditorField : QgsAttributeEditorElement
{
%TypeHeaderCode
#include "qgsvectorlayer.h"
%End

  public:
    QgsAttributeEditorField( QString name , int idx, QObject *parent );
    ~QgsAttributeEditorField();

    virtual QDomElement toDomElement( QDomDocument& doc ) const;
    int idx() const;
};

/** @note added in 1.7 */
struct QgsVectorJoinInfo
{
%TypeHeaderCode
#include "qgsvectorlayer.h"
%End

  /**Join field in the target layer*/
  QString targetFieldName;
  /**Source layer*/
  QString joinLayerId;
  /**Join field in the source layer*/
  QString joinFieldName;
  /**True if the join is cached in virtual memory*/
  bool memoryCache;
  /**Cache for joined attributes to provide fast lookup (size is 0 if no memory caching)
    @note not available in python bindings
    */
  // QHash< QString, QgsAttributeMap> cachedAttributes;
};


class QgsVectorLayer : QgsMapLayer
{
%TypeHeaderCode
#include "qgsvectorlayer.h"
%End

  public:

    enum EditorLayout
    {
      GeneratedLayout,
      TabLayout,
      UiFileLayout,
    };

    enum EditType
    {
      LineEdit,
      UniqueValues,
      UniqueValuesEditable,
      ValueMap,
      Classification,
      EditRange,
      SliderRange,
      CheckBox,      /* added in 1.4 */
      FileName,
      Enumeration,
      Immutable,     /* The attribute value should not be changed in the attribute form */
      Hidden,        /* The attribute value should not be shown in the attribute form @added in 1.4 */
      TextEdit,      /* multiline edit @added in 1.4*/
      Calendar,      /* calendar widget @added in 1.5 */
      DialRange,     /* dial range @added in 1.5 */
      ValueRelation, /* value map from an table @added in 1.8 */
      UuidGenerator, /* uuid generator - readonly and automatically intialized @added in 1.9 */
      Photo,         /* phote widget @added in 1.9 */
      WebView,       /* webview widget @added in 1.9 */
      Color,         /* color @added in 1.9 */
    };

    struct RangeData
    {
      RangeData();
      RangeData( QVariant theMin, QVariant theMax, QVariant theStep );

      QVariant mMin;
      QVariant mMax;
      QVariant mStep;
    };

    struct ValueRelationData
    {
      ValueRelationData();
      ValueRelationData( QString layer, QString key, QString value, bool allowNull, bool orderByValue,
                         bool allowMulti = false,
                         QString filterExpression = QString::null );

      QString mLayer;
      QString mKey;
      QString mValue;
      QString mFilterExpression;
      bool mAllowNull;
      bool mOrderByValue;
      bool mAllowMulti;  /* allow selection of multiple keys @added in 1.9 */
    };

    struct GroupData
    {
      GroupData();
      GroupData( QString name , QList<QString> fields );
      QString mName;
      QList<QString> mFields;
    };

    struct TabData
    {
      TabData();
      TabData( QString name , QList<QString> fields , QList<QgsVectorLayer::GroupData> groups );
      QString mName;
      QList<QString> mFields;
      QList<QgsVectorLayer::GroupData> mGroups;
    };

    /** Constructor */
    QgsVectorLayer( QString path = QString::null, QString baseName = QString::null,
                    QString providerLib = QString::null, bool loadDefaultStyleFlag = true );

    /** Destructor */
    virtual ~QgsVectorLayer();

    /** Returns the permanent storage type for this layer as a friendly name. */
    QString storageType() const;

    /** Capabilities for this layer in a friendly format. */
    QString capabilitiesString() const;

    /** Returns a comment for the data in the layer */
    QString dataComment() const;

    /** Set the primary display field to be used in the identify results dialog */
    void setDisplayField( QString fldName = "" );

    /** Returns the primary display field name used in the identify results dialog */
    const QString displayField() const;

    /** Returns the data provider */
    QgsVectorDataProvider* dataProvider();

    /** Returns the data provider in a const-correct manner
        @note not available in python bindings
      */
    //const QgsVectorDataProvider* dataProvider() const;

    /** Sets the textencoding of the data provider */
    void setProviderEncoding( const QString& encoding );

    /** Setup the coordinate system tranformation for the layer */
    void setCoordinateSystem();

    /** Joins another vector layer to this layer
      @param joinInfo join object containing join layer id, target and source field
      @note added in 1.7 */
    void addJoin( QgsVectorJoinInfo joinInfo );

    /** Removes  a vector layer join
      @note added in 1.7 */
    void removeJoin( const QString& joinLayerId );

    /** @note added in 1.7 */
    const QList< QgsVectorJoinInfo >& vectorJoins() const;

    /** Get the label object associated with this layer */
    QgsLabel *label();

    // const QgsLabel *label() const;

    QgsAttributeAction *actions();

    /** The number of features that are selected in this layer */
    int selectedFeatureCount();

    /**
     * Select features found within the search rectangle (in layer's coordinates)
     *
     * @param rect            The search rectangle
     * @param addToSelection  If set to true will not clear before selecting
     */
    void select( QgsRectangle & rect, bool addToSelection );

    /**
     * Modifies the current selection on this layer
     *
     * @param selectIds    Select these ids
     * @param deselectIds  Deselect these ids
     */
    void modifySelection(QgsFeatureIds selectIds, QgsFeatureIds deselectIds );

    /** Select not selected features and deselect selected ones */
    void invertSelection();

    /** Invert selection of features found within the search rectangle (in layer's coordinates) */
    void invertSelectionInRectangle( QgsRectangle & rect );

    /** Get a copy of the user-selected features */
    QList<QgsFeature> selectedFeatures();

    /** Return reference to identifiers of selected features */
    const QgsFeatureIds &selectedFeaturesIds() const;

    /** Change selection to the new set of features */
    void setSelectedFeatures( const QgsFeatureIds &ids );

    /** Returns the bounding box of the selected features. If there is no selection, QgsRectangle(0,0,0,0) is returned */
    QgsRectangle boundingBoxOfSelected();

    /** Sets diagram rendering object (takes ownership) */
    void setDiagramRenderer( QgsDiagramRendererV2* r /Transfer/ );
    const QgsDiagramRendererV2* diagramRenderer() const;

    void setDiagramLayerSettings( const QgsDiagramLayerSettings& s );
    const QgsDiagramLayerSettings *diagramLayerSettings() const;

    /** Return renderer V2.
     * @note added in 1.4 */
    QgsFeatureRendererV2* rendererV2();
    /** Set renderer V2.
     * @note added in 1.4
     */
    void setRendererV2( QgsFeatureRendererV2* r /Transfer/ );

    /** Draw layer with renderer V2.
     * @note added in 1.4
     */
    void drawRendererV2( QgsFeatureIterator &fit, QgsRenderContext& rendererContext, bool labeling );

    /** Draw layer with renderer V2 using symbol levels.
     * @note added in 1.4
     */
    void drawRendererV2Levels( QgsFeatureIterator &fit, QgsRenderContext& rendererContext, bool labeling );

    /** Returns point, line or polygon */
    QGis::GeometryType geometryType() const;

    /** Returns true if this is a geometry layer and false in case of NoGeometry (table only) or UnknownGeometry
     * @note added in 1.7
     */
    bool hasGeometryType() const;

    /**Returns the WKBType or WKBUnknown in case of error*/
    QGis::WkbType wkbType() const;

    /** Return the provider type for this layer */
    QString providerType() const;

    /** reads vector layer specific state from project file Dom node.
     *  @note Called by QgsMapLayer::readXML().
     */
    virtual bool readXml( const QDomNode& layer_node );

    /** write vector layer specific state to project file Dom node.
     *  @note Called by QgsMapLayer::writeXML().
     */
    virtual bool writeXml( QDomNode & layer_node, QDomDocument & doc );

    /** convert a saved attribute editor element into a AttributeEditor structure as it's used internally.
     * @param elem the DOM element
     * @param parent the QObject which will own this object
     */
    QgsAttributeEditorElement* attributeEditorElementFromDomElement( QDomElement &elem, QObject* parent );

    /** Read the symbology for the current layer from the Dom node supplied.
     * @param node node that will contain the symbology definition for this layer.
     * @param errorMessage reference to string that will be updated with any error messages
     * @return true in case of success.
     */
    bool readSymbology( const QDomNode& node, QString& errorMessage );

    /** Write the symbology for the layer into the docment provided.
     *  @param node the node that will have the style element added to it.
     *  @param doc the document that will have the QDomNode added.
     *  @param errorMessage reference to string that will be updated with any error messages
     *  @return true in case of success.
     */
    bool writeSymbology( QDomNode& node, QDomDocument& doc, QString& errorMessage ) const;

    bool writeSld( QDomNode& node, QDomDocument& doc, QString& errorMessage ) const;
    bool readSld( const QDomNode& node, QString& errorMessage );

    /**
     * Number of features in the layer. This is necessary if features are
     * added/deleted or the layer has been subsetted. If the data provider
     * chooses not to support this feature, the total number of features
     * can be returned.
     * @return long containing number of features
     */
    virtual long featureCount() const;

    /**
     * Number of features rendered with specified symbol. Features must be first
     * calculated by countSymbolFeatures()
     * @param symbol the symbol
     * @return number of features rendered by symbol or -1 if failed or counts are not available
     */
    long featureCount( QgsSymbolV2* symbol );

    /**
     * Count features for symbols. Feature counts may be get by featureCount( QgsSymbolV2*).
     * @param showProgress show progress dialog
     * @return true if calculated, false if failed or was canceled by user
     */
    bool countSymbolFeatures( bool showProgress = true );

    /**
     * Set the string (typically sql) used to define a subset of the layer
     * @param subset The subset string. This may be the where clause of a sql statement
     *               or other defintion string specific to the underlying dataprovider
     *               and data store.
     * @return true, when setting the subset string was successful, false otherwise (added in 1.4)
     */
    virtual bool setSubsetString( QString subset );

    /**
     * Get the string (typically sql) used to define a subset of the layer
     * @return The subset string or QString::null if not implemented by the provider
     */
    virtual QString subsetString();

    /**
     * Query the provider for features specified in request.
     */
    QgsFeatureIterator getFeatures( const QgsFeatureRequest& request = QgsFeatureRequest() );

    /** Adds a feature
        @param f feature to add
        @param alsoUpdateExtent If True, will also go to the effort of e.g. updating the extents.
        @return                    True in case of success and False in case of error
     */
    bool addFeature( QgsFeature& f, bool alsoUpdateExtent = true );

    /** Updates an existing feature
        @param f feature to update
        @return                    True in case of success and False in case of error
        @note added in 1.8
     */
    bool updateFeature( QgsFeature &f );

    /** Insert a new vertex before the given vertex number,
     *  in the given ring, item (first number is index 0), and feature
     *  Not meaningful for Point geometries
     */
    bool insertVertex( double x, double y, QgsFeatureId atFeatureId, int beforeVertex );

    /** Moves the vertex at the given position number,
     *  ring and item (first number is index 0), and feature
     *  to the given coordinates
     */
    bool moveVertex( double x, double y, QgsFeatureId atFeatureId, int atVertex );

    /** Deletes a vertex from a feature
     */
    bool deleteVertex( QgsFeatureId atFeatureId, int atVertex );

    /** Deletes the selected features
     *  @return true in case of success and false otherwise
     */
    bool deleteSelectedFeatures();

    /**Adds a ring to polygon/multipolygon features
     @return
       0 in case of success,
       1 problem with feature type,
       2 ring not closed,
       3 ring not valid,
       4 ring crosses existing rings,
       5 no feature found where ring can be inserted
       6 layer not editable */
    int addRing( const QList<QgsPoint>& ring );

    /**Adds a new part polygon to a multipart feature
     @return
       0 in case of success,
       1 if selected feature is not multipart,
       2 if ring is not a valid geometry,
       3 if new polygon ring not disjoint with existing rings,
       4 if no feature was selected,
       5 if several features are selected,
       6 if selected geometry not found
       7 layer not editable */
    int addPart( const QList<QgsPoint>& ring );

    /**Translates feature by dx, dy
       @param featureId id of the feature to translate
       @param dx translation of x-coordinate
       @param dy translation of y-coordinate
       @return 0 in case of success*/
    int translateFeature( QgsFeatureId featureId, double dx, double dy );

    /**Splits features cut by the given line
     *  @param splitLine line that splits the layer features
     *  @param topologicalEditing true if topological editing is enabled
     *  @return
     *   0 in case of success,
     *   4 if there is a selection but no feature split
     */
    int splitFeatures( const QList<QgsPoint>& splitLine, bool topologicalEditing = false );

    /**Changes the specified geometry such that it has no intersections with other
     *  polygon (or multipolygon) geometries in this vector layer
     *  @param geom geometry to modify
     *  @param ignoreFeatures list of feature ids where intersections should be ignored
     *  @return 0 in case of success
     */
    int removePolygonIntersections( QgsGeometry* geom, QgsFeatureIds ignoreFeatures = QgsFeatureIds() );

    /** Adds topological points for every vertex of the geometry.
     * @param geom the geometry where each vertex is added to segments of other features
     * @note geom is not going to be modified by the function
     * @return 0 in case of success
     */
    int addTopologicalPoints( QgsGeometry* geom );

    /** Adds a vertex to segments which intersect point p but don't
     * already have a vertex there. If a feature already has a vertex at position p,
     * no additional vertex is inserted. This method is useful for topological
     * editing.
     * @param p position of the vertex
     * @return 0 in case of success
     */
    int addTopologicalPoints( const QgsPoint& p );

    /**Inserts vertices to the snapped segments.
     * This is useful for topological editing if snap to segment is enabled.
     * @param snapResults results collected from the snapping operation
     * @return 0 in case of success
     */
    int insertSegmentVerticesForSnap( const QList<QgsSnappingResult>& snapResults );

    /** Set labels on */
    void enableLabels( bool on );

    /** Label is on */
    bool hasLabelsEnabled() const;

    /** Returns true if the provider is in editing mode */
    virtual bool isEditable() const;

    /** Returns true if the provider is in read-only mode
     * @note added in 1.6
     */
    virtual bool isReadOnly() const;

    /** Returns true if the provider has been modified since the last commit */
    virtual bool isModified() const;

    /**Snaps a point to the closest vertex if there is one within the snapping tolerance
     *  @param point       The point which is set to the position of a vertex if there is one within the snapping tolerance.
     *  If there is no point within this tolerance, point is left unchanged.
     *  @param tolerance   The snapping tolerance
     *  @return true if the point has been snapped, false if no vertex within search tolerance
     */
    bool snapPoint( QgsPoint& point, double tolerance );

    /**Snaps to segment or vertex within given tolerance
     * @param startPoint point to snap (in layer coordinates)
     * @param snappingTolerance distance tolerance for snapping
     * @param snappingResults snapping results. Key is the distance between startPoint and snapping target
     * @param snap_to to segment / to vertex
     * @return 0 in case of success
     */
    int snapWithContext( const QgsPoint& startPoint,
                         double snappingTolerance,
                         QMultiMap < double, QgsSnappingResult > &snappingResults /Out/,
                         QgsSnapper::SnappingType snap_to );

    /**Synchronises with changes in the datasource
      @note added in version 1.6*/
    virtual void reload();

    /** Draws the layer
     *  @return false if an error occurred during drawing
     */
    bool draw( QgsRenderContext& rendererContext );

    /** Draws the layer labels using coordinate transformation */
    void drawLabels( QgsRenderContext& rendererContext );

    /** Return the extent of the layer as a QRect */
    QgsRectangle extent();

    /** returns field list in the to-be-committed state */
    const QgsFields &pendingFields() const;

    /** returns list of attributes */
    QList<int> pendingAllAttributesList();

    /** returns list of attribute making up the primary key
     * @note added in 2.0
     */
    QList<int> pendingPkAttributesList();

    /** returns feature count after commit */
    int pendingFeatureCount();

    /** Make layer read-only (editing disabled) or not
     *  @return false if the layer is in editing yet
     *  @note added in 1.6
     */
    bool setReadOnly( bool readonly = true );

    /** Make layer editable */
    bool startEditing();

    /** change feature's geometry
      @note added in version 1.2 */
    bool changeGeometry( QgsFeatureId fid, QgsGeometry* geom );

    /** changed an attribute value (but does not commit it) */
    bool changeAttributeValue( QgsFeatureId fid, int field, QVariant value, bool emitSignal = true );

    /** add an attribute field (but does not commit it)
        returns true if the field was added
      @note added in version 1.2 */
    bool addAttribute( const QgsField &field );

    /**Sets an alias (a display name) for attributes to display in dialogs
      @note added in version 1.2*/
    void addAttributeAlias( int attIndex, QString aliasString );

    /**Adds a tab (for the attribute editor form) holding groups and fields
      @note added in version 1.9*/
    void addAttributeEditorWidget( QgsAttributeEditorElement* data );
    /**Returns a list of tabs holding groups and fields
      @note added in version 1.9*/
    QList< QgsAttributeEditorElement* > &attributeEditorElements();
    /**Clears all the tabs for the attribute editor form
      @note added in version 1.9*/
    void clearAttributeEditorWidgets();

    /**Returns the alias of an attribute name or an empty string if there is no alias
      @note added in version 1.2*/
    QString attributeAlias( int attributeIndex ) const;

    /**Convenience function that returns the attribute alias if defined or the field name else
      @note added in version 1.2*/
    QString attributeDisplayName( int attributeIndex ) const;

    const QMap< QString, QString >& attributeAliases() const;

    const QSet<QString>& excludeAttributesWMS() const;
    void setExcludeAttributesWMS( const QSet<QString>& att );

    const QSet<QString>& excludeAttributesWFS() const;
    void setExcludeAttributesWFS( const QSet<QString>& att );

    /** delete an attribute field (but does not commit it) */
    bool deleteAttribute( int attr );

    /**
     * Deletes a list of attribute fields (but does not commit it)
     *
     * @param  attrs the indices of the attributes to delete
     * @return true if at least one attribute has been deleted
     *
     */
    bool deleteAttributes( QList<int> attrs );

    /** Insert a copy of the given features into the layer  (but does not commit it) */
    bool addFeatures( QList<QgsFeature> features, bool makeSelected = true );

    /** delete a feature from the layer (but does not commit it) */
    bool deleteFeature( QgsFeatureId fid );

    /**
      Attempts to commit any changes to disk.  Returns the result of the attempt.
      If a commit fails, the in-memory changes are left alone.

      This allows editing to continue if the commit failed on e.g. a
      disallowed value in a Postgres database - the user can re-edit and try
      again.

      The commits occur in distinct stages,
      (add attributes, add features, change attribute values, change
      geometries, delete features, delete attributes)
      so if a stage fails, it's difficult to roll back cleanly.
      Therefore any error message also includes which stage failed so
      that the user has some chance of repairing the damage cleanly.
     */
    bool commitChanges();
    const QStringList &commitErrors();

    /** Stop editing and discard the edits
     * @param deleteBuffer whether to delete editing buffer (added in 1.9)
     */
    bool rollBack( bool deleteBuffer = true );

    /**get edit type*/
    EditType editType( int idx );

    /**set edit type*/
    void setEditType( int idx, EditType edit );

    /** get the active layout for the attribute editor for this layer (added in 1.9) */
    EditorLayout editorLayout();

    /** set the active layout for the attribute editor for this layer (added in 1.9) */
    void setEditorLayout( EditorLayout editorLayout );

    /** set string representing 'true' for a checkbox (added in 1.4) */
    void setCheckedState( int idx, QString checked, QString notChecked );

    /** return string representing 'true' for a checkbox (added in 1.4)
     * @note not available in python bindings
     * FIXME: need SIP binding for QPair<QString, QString>
     */
    // QPair<QString, QString> checkedState( int idx );

    /** get edit form (added in 1.4) */
    QString editForm();

    /** set edit form (added in 1.4) */
    void setEditForm( QString ui );

    /** get annotation form (added in 1.5)*/
    QString annotationForm() const;

    /** set annotation form for layer (added in 1.5)*/
    void setAnnotationForm( const QString& ui );

    /** get python function for edit form initialization (added in 1.4) */
    QString editFormInit();

    /** set python function for edit form initialization (added in 1.4) */
    void setEditFormInit( QString function );

    /**access value map*/
    QMap<QString, QVariant> &valueMap( int idx );

    /**access range */
    RangeData &range( int idx );

    /**access relations
     * @note added in 1.8
     **/
    ValueRelationData &valueRelation( int idx );

    /**access date format
     * @note added in 1.9
     */
    QString &dateFormat( int idx );

    /**access widget size for photo and webview widget
     * @note added in 1.9
     */
    QSize &widgetSize( int idx );

    /**is edit widget editable
     * @note added in 1.9
     **/
    bool fieldEditable( int idx );

    /**set edit widget editable
     * @note added in 1.9
     **/
    void setFieldEditable( int idx, bool editable );

    /**Adds a new overlay to this class. QgsVectorLayer takes ownership of the object
     @note this method was added in version 1.1
     */
    void addOverlay( QgsVectorOverlay* overlay /Transfer/ );

    /**Removes all overlays of a given type
    @note this method was added in version 1.1
    */
    void removeOverlay( const QString& typeName );

    /**Returns pointers to the overlays of this layer
    @note this method was added in version 1.1
    */
    void vectorOverlays( QList<QgsVectorOverlay*>& overlayList /Out/ );

    /**Returns the (first) overlay of a type, e.g. diagram or label
    @note this method was added in version 1.1
    */
    QgsVectorOverlay* findOverlayByType( const QString& typeName );

    //! Buffer with uncommitted editing operations. Only valid after editing has been turned on.
    QgsVectorLayerEditBuffer* editBuffer();

    /**
     * Create edit command for undo/redo operations
     * @param text text which is to be displayed in undo window
     */
    void beginEditCommand( QString text );

    /** Finish edit command and add it to undo/redo stack */
    void endEditCommand();

    /** Destroy active command and reverts all changes in it */
    void destroyEditCommand();

    /** Returns the index of a field name or -1 if the field does not exist
      @note this method was added in version 1.4
     */
    int fieldNameIndex( const QString& fieldName ) const;

    /** Editing vertex markers
      @note public from version 1.4 */
    enum VertexMarkerType
    {
      SemiTransparentCircle,
      Cross,
      NoMarker  /* added in version 1.1 */
    };

    /** Draws a vertex symbol at (screen) coordinates x, y. (Useful to assist vertex editing.)
      @note public and static from version 1.4 */
    static void drawVertexMarker( double x, double y, QPainter& p, QgsVectorLayer::VertexMarkerType type, int vertexSize );

    /** Assembles mUpdatedFields considering provider fields, joined fields and added fields
     @note added in 1.7 */
    void updateFields();

    /** Caches joined attributes if required (and not already done)
      @note added in 1.7 */
    void createJoinCaches();

    /**Returns unique values for column
      @param index column index for attribute
      @param uniqueValues out: result list
      @param limit maximum number of values to return (-1 if unlimited)
      @note this method was added in version 1.7 */
    void uniqueValues( int index, QList<QVariant> &uniqueValues /Out/, int limit = -1 );

    /**Returns minimum value for an attribute column or invalid variant in case of error
      @note added in 1.7*/
    QVariant minimumValue( int index );

    /**Returns maximum value for an attribute column or invalid variant in case of error
      @note added in 1.7*/
    QVariant maximumValue( int index );

  public slots:
    /**
     * Select feature by its ID
     *
     * @param featureId  The id of the feature to select
     */
    void select( QgsFeatureId featureId );

    /**
     * Select features by their ID
     *
     * @param featureIds The ids of the features to select
     */
    void select( QgsFeatureIds featureIds );

    /**
     * Deselect feature by its ID
     *
     * @param featureId  The id of the feature to deselect
     */
    void deselect( QgsFeatureId featureId );

    /**
     * Deselect features by their ID
     *
     * @param featureIds The ids of the features to deselect
     */
    void deselect( QgsFeatureIds featureIds );

    /** Clear selection */
    void removeSelection();

    void triggerRepaint();

    /** Update the extents for the layer. This is necessary if features are
     *  added/deleted or the layer has been subsetted.
     */
    virtual void updateExtents();

    /** Check if there is a join with a layer that will be removed
      @note added in 1.7 */
    void checkJoinLayerRemove( QString theLayerId );

    QString metadata();

  signals:

    /** This signal is emited when selection was changed */
    void selectionChanged();

    /** This signal is emitted when modifications has been done on layer */
    void layerModified();

    void editingStarted();
    void editingStopped();

    /**
     * Will be emitted, when a new attribute has been added to this vector layer.
     * Applies only to types {@link QgsFields::OriginEdit} and {@link QgsFields::OriginProvider}
     *
     * @param The index of the new attribute
     *
     * @see updatedFields()
     */
    void attributeAdded( int idx );

    /**
     * Will be emitted, when an attribute has been deleted from this vector layer.
     * Applies only to types {@link QgsFields::OriginEdit} and {@link QgsFields::OriginProvider}
     *
     * @param The index of the deleted attribute
     *
     * @see updatedFields()
     */
    void attributeDeleted( int idx );
    void featureAdded( QgsFeatureId fid );  // added in 1.7

    /**
     * Is emitted, whenever the fields available from this layer have been changed.
     * This can be due to manually adding attributes or due to a join.
     */
    void updatedFields();

    void featureDeleted( QgsFeatureId fid );
    void layerDeleted();

    void attributeValueChanged( QgsFeatureId fid, int idx, const QVariant & );
    void geometryChanged( QgsFeatureId fid, QgsGeometry &geom ); // added in 1.9

    /** Signals emitted after committing changes
      \note added in v1.6 */
    void committedAttributesDeleted( const QString& layerId, const QgsAttributeList& deletedAttributes );
    void committedAttributesAdded( const QString& layerId, const QList<QgsField>& addedAttributes );
    void committedFeaturesAdded( const QString& layerId, const QgsFeatureList& addedFeatures );
    void committedFeaturesRemoved( const QString& layerId, const QgsFeatureIds& deletedFeatureIds );
    void committedAttributeValuesChanges( const QString& layerId, const QgsChangedAttributesMap& changedAttributesValues );
    void committedGeometriesChanges( const QString& layerId, const QgsGeometryMap& changedGeometries );

  protected:
    /** Set the extent */
    void setExtent( const QgsRectangle &rect );

  private:                       // Private methods

    /** vector layers are not copyable */
    QgsVectorLayer( const QgsVectorLayer & rhs );



};

