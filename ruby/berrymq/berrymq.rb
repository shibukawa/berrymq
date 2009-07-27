require 'set'

module BerryMQ
  class Identifier
    attr_reader :name, :action, :namespace
    def initialize(key_or_identifier, action=nil)
      @functions = [nil, nil]
      if action != nil
        @name = key_or_identifier
        @action = Set.new [action]
        @functions[0] = method :_match_all
        return
      end
      name, @namespace, action = _split_key(key_or_identifier)
      if name == "*" && action == "*"
        @name = @action = nil
        @functions[0] = method :_match_always
      elsif name == "*" && action != "*"
        @name = nil
        @action = Set.new [$2]
        @functions[0] = method :_match_action_only
      elsif name != "*" && action == "*"
        @name = name
        @action = nil
        @functions[0] = method :_match_name_only
      elsif name != "*" && action != "*"
        @name = name
        @action = Set.new [$2]
        @functions[0] = method :_match_all
      end
      @functions[1] = method :_match_always
    end

    def _split_key(key)
      if /(.*):(.*)/ =~ key
        name = $1
        action = $2
      else
        name = key
        action = "*"
      end
      if /(.*)@(.*)/ =~ name
        name = $1
        namespace = $2
      else
        namespace = nil
      end
      return [name, namespace, action]
    end

    def guard(&condition)
      @functions[1] = condition
    end

    def to_s
      "<mqas.Identifier object at %d: id=%s>" % [self.object_id, id_str()]
    end

    def id_str
      name = @name || "*"
      action = @action != nil ? @action.to_a.sort.join(",") : "*"
      "%s:%s" % [name, action]
    end

    def _match_all(rhs)
      _match_name_only(rhs) && _match_action_only(rhs)
    end

    def _match_name_only(rhs)
      self.name == rhs.name
    end

    def _match_always(p)
      true
    end

    def _match_action_only(rhs)
      if self.action == nil
        rhs.action != nil
      elsif rhs.action == nil
        self.action != nil
      else
        !(self.action && rhs.action).empty?
      end
    end

    def is_match(expose_identifier, message=nil)
      if @functions[0].call(expose_identifier)      
        @functions[1].call(message) 
      else
        false
      end
    end

    def is_local
      @name.slice(0,1) == "_"
    end
  end

  class Follower
    def __following(key)
  end

  class MessageQueue
    def initialize
      @followers = Hash.new do [] end
    end

    def regist_follower(id_obj, function)
      @followers[id_obj.name].push([id_obj, function])
    end

    def twitter(id_obj, args, kwargs)
      twitter_local(id_obj, args, kwargs)
    end

    def twitter_local(id_obj, args, kwargs)
      message = Message(id_obj, args, kwargs, counter)
    end
  end

  class Message
    attr_reader :args, kwargs
    def initialize(id_obj, args, kwargs)
      @id_obj = id_obj
      @args = args
      @kwargs = kwargs
    end
    def name
      @id_obj.name
    end
    def action
      @id_obj.action
    end
    def id
      @id_obj.id_str()
    end
    def twitter(id_obj, args, kwargs)
      MessageQueueRoot.twitter(id_obj, args, kwargs)
    end
    def apply(func)
    end
  end

  module MessageQueueRoot
    @@namespaces = Hash.new do MessageQueue.new end
    MessageQueueRoot.twitter(id_obj, args, kwargs)
  end

  def twitter(id_obj, *args)

  end
end
