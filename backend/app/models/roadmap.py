from datetime import datetime
from app.models import db

class Roadmap(db.Model):
    __tablename__ = 'roadmaps'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(128), unique=True, nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    nodes = db.relationship('RoadmapNode', backref='roadmap', cascade='all, delete-orphan', order_by='RoadmapNode.order_index')

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'nodes_count': len(self.nodes)
        }

class RoadmapNode(db.Model):
    __tablename__ = 'roadmap_nodes'

    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmaps.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('roadmap_nodes.id', ondelete='SET NULL'), nullable=True)
    label = db.Column(db.String(128), nullable=False)
    description_markdown = db.Column(db.Text, nullable=True)
    node_type = db.Column(db.String(32), default='topic')  # 'section', 'topic', 'subtopic'
    importance = db.Column(db.String(32), default='recommended')  # 'recommended', 'alternative', 'optional'
    order_index = db.Column(db.Integer, default=1)
    layout_group = db.Column(db.String(64), nullable=True)  # 'fundamentals', 'red_team', 'blue_team', 'cloud', etc.
    position_x = db.Column(db.Float, nullable=True)
    position_y = db.Column(db.Float, nullable=True)

    # Relationships
    resources = db.relationship('RoadmapNodeResource', backref='node', cascade='all, delete-orphan', order_by='RoadmapNodeResource.order_index')
    children = db.relationship('RoadmapNode', backref=db.backref('parent', remote_side=[id]), cascade='all, delete-orphan')

    def to_dict(self, user_status_map=None):
        status = 'not_started'
        if user_status_map and self.id in user_status_map:
            status = user_status_map[self.id]

        return {
            'id': self.id,
            'roadmap_id': self.roadmap_id,
            'parent_id': self.parent_id,
            'label': self.label,
            'description_markdown': self.description_markdown or '',
            'node_type': self.node_type or 'topic',
            'importance': self.importance or 'recommended',
            'order_index': self.order_index,
            'layout_group': self.layout_group,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'resources': [r.to_dict() for r in self.resources],
            'user_status': status
        }

class RoadmapNodeResource(db.Model):
    __tablename__ = 'roadmap_node_resources'

    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('roadmap_nodes.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    resource_type = db.Column(db.String(32), default='article')  # 'article', 'video', 'doc'
    order_index = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'node_id': self.node_id,
            'title': self.title,
            'url': self.url,
            'resource_type': self.resource_type or 'article',
            'order_index': self.order_index
        }

class RoadmapEdge(db.Model):
    __tablename__ = 'roadmap_edges'

    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmaps.id', ondelete='CASCADE'), nullable=False)
    source_node_id = db.Column(db.Integer, db.ForeignKey('roadmap_nodes.id', ondelete='CASCADE'), nullable=False)
    target_node_id = db.Column(db.Integer, db.ForeignKey('roadmap_nodes.id', ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(128), nullable=True)
    edge_type = db.Column(db.String(32), default='default')  # 'default', 'prerequisite', 'alternative'
    order_index = db.Column(db.Integer, default=1)

    __table_args__ = (
        db.UniqueConstraint('source_node_id', 'target_node_id', name='_edge_source_target_uc'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'roadmap_id': self.roadmap_id,
            'source_node_id': self.source_node_id,
            'target_node_id': self.target_node_id,
            'label': self.label,
            'edge_type': self.edge_type or 'default',
            'order_index': self.order_index
        }

class UserRoadmapProgress(db.Model):
    __tablename__ = 'user_roadmap_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    node_id = db.Column(db.Integer, db.ForeignKey('roadmap_nodes.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(32), default='not_started')  # 'not_started', 'in_progress', 'done'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'node_id', name='_user_node_uc'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'node_id': self.node_id,
            'status': self.status,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
